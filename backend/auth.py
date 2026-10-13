"""Invite-only access.

* Accounts are created by the owner (`python -m backend.cli create-user`), there is no
  public sign-up.
* Login sets an httpOnly cookie with a random token; the database stores only its hash,
  so a leaked database can't be used to log in, and logout really revokes the session.
* Anonymous visitors see the read-only demo workspace. Any write in demo mode returns
  403 with code `demo_read_only`, which the UI turns into a "Request access" dialog.
"""

import hashlib
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response
from pwdlib import PasswordHash
from sqlmodel import Session, col, select

from backend.config import get_settings
from backend.database import SessionDep
from backend.models import User, UserSession, utcnow

COOKIE_NAME = "rs_session"
DEMO_EMAIL = "demo@rivalscope.local"
_hasher = PasswordHash.recommended()


def api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message})


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return bool(password_hash) and _hasher.verify(password, password_hash)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(session: Session, user_id: int, response: Response) -> None:
    settings = get_settings()
    token = secrets.token_urlsafe(32)
    expires = utcnow() + timedelta(days=settings.session_days)
    session.add(UserSession(token_hash=_token_hash(token), user_id=user_id, expires_at=expires))
    session.commit()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def end_session(session: Session, request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        stored = session.get(UserSession, _token_hash(token))
        if stored:
            session.delete(stored)
            session.commit()
    response.delete_cookie(COOKIE_NAME, path="/")


def get_optional_user(request: Request, session: SessionDep) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    stored = session.get(UserSession, _token_hash(token))
    if stored is None or stored.expires_at < utcnow():
        return None
    return session.get(User, stored.user_id)


def ensure_demo_user(session: Session) -> User:
    demo = session.exec(select(User).where(col(User.is_demo).is_(True))).first()
    if demo is None:
        demo = User(email=DEMO_EMAIL, is_demo=True)
        session.add(demo)
        session.commit()
        session.refresh(demo)
    return demo


@dataclass
class Workspace:
    user: User
    read_only: bool

    def require_write(self) -> None:
        if self.read_only:
            raise api_error(
                403,
                "demo_read_only",
                "This is a read-only demo. Request access to monitor your own products.",
            )


def get_workspace(
    session: SessionDep, user: Annotated[User | None, Depends(get_optional_user)]
) -> Workspace:
    if user is not None:
        return Workspace(user=user, read_only=user.is_demo)
    return Workspace(user=ensure_demo_user(session), read_only=True)


def get_current_user(user: Annotated[User | None, Depends(get_optional_user)]) -> User:
    if user is None:
        raise api_error(401, "not_authenticated", "Please sign in.")
    return user


WorkspaceDep = Annotated[Workspace, Depends(get_workspace)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class RateLimiter:
    """Tiny in-memory limiter (per client IP) for login and the public contact form."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit, self.window = limit, window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, request: Request) -> None:
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self.hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            raise api_error(429, "rate_limited", "Too many attempts. Please try again later.")
        hits.append(now)
