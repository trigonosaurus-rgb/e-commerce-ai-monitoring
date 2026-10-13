"""Sign in/out, notification settings, access requests, public metadata and health."""

import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Request, Response
from sqlalchemy import text
from sqlmodel import func, select

from backend import notify
from backend.api.schemas import AccessRequestIn, LoginIn, NotificationSettings
from backend.auth import (
    CurrentUser,
    RateLimiter,
    WorkspaceDep,
    api_error,
    create_session,
    end_session,
    verify_password,
)
from backend.config import get_settings
from backend.database import SessionDep
from backend.models import AccessRequest, User
from backend.notify.telegram import bot_username, poller
from backend.scheduler import scheduler

router = APIRouter(tags=["account"])
login_limiter = RateLimiter(limit=10, window_seconds=15 * 60)
contact_limiter = RateLimiter(limit=3, window_seconds=60 * 60)


# ---------------------------------------------------------------------------- auth


@router.post("/auth/login")
def login(body: LoginIn, request: Request, response: Response, session: SessionDep):
    login_limiter.check(request)
    user = session.exec(select(User).where(func.lower(User.email) == body.email.lower())).first()
    if user is None or user.is_demo or not verify_password(body.password, user.password_hash):
        raise api_error(401, "bad_credentials", "Wrong email or password.")
    create_session(session, user.id, response)
    return {"email": user.email}


@router.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response, session: SessionDep):
    end_session(session, request, response)


@router.get("/auth/me")
def me(ws: WorkspaceDep):
    return {"email": None if ws.read_only else ws.user.email, "demo": ws.read_only}


# ------------------------------------------------------------------- notifications


def _notification_state(user: User) -> dict:
    settings = get_settings()
    return {
        "notify_email": user.notify_email,
        "alert_email": user.alert_email or user.email,
        "notify_telegram": user.notify_telegram,
        "telegram_connected": bool(user.telegram_chat_id),
        "telegram_available": settings.telegram_configured and bool(bot_username()),
        "email_available": settings.email_configured,
    }


@router.get("/settings/notifications")
def get_notifications(user: CurrentUser):
    return _notification_state(user)


@router.put("/settings/notifications")
def update_notifications(body: NotificationSettings, user: CurrentUser, session: SessionDep):
    user = session.merge(user)
    user.notify_email = body.notify_email
    user.alert_email = str(body.alert_email) if body.alert_email else None
    user.notify_telegram = body.notify_telegram and bool(user.telegram_chat_id)
    session.commit()
    return _notification_state(user)


@router.post("/settings/telegram/link")
def telegram_link(user: CurrentUser, session: SessionDep):
    settings = get_settings()
    if not (settings.telegram_configured and bot_username()):
        raise api_error(503, "not_configured", "Telegram alerts are not set up on this server.")
    user = session.merge(user)
    user.telegram_link_token = secrets.token_urlsafe(16)
    session.commit()
    return {"url": f"https://t.me/{bot_username()}?start={user.telegram_link_token}"}


@router.post("/settings/telegram/unlink")
def telegram_unlink(user: CurrentUser, session: SessionDep):
    user = session.merge(user)
    user.telegram_chat_id = None
    user.notify_telegram = False
    session.commit()
    return _notification_state(user)


@router.post("/settings/notifications/test")
async def test_notification(user: CurrentUser):
    if not (user.notify_email or user.notify_telegram):
        raise api_error(400, "no_channels", "Turn on at least one channel first.")
    app = get_settings().app_name
    results = await notify.send_to_user(
        user,
        # a unique subject, so mail apps don't fold repeated tests into one conversation
        f"Test alert from {app} · {datetime.now(UTC):%H:%M:%S} UTC",
        "If you can read this, price alerts will reach you here.",
        [{"label": f"Open {app}", "url": notify.app_link("/")}],
    )
    return {"results": results}


# ----------------------------------------------------------------- public endpoints


@router.post("/access-requests", status_code=201)
async def request_access(body: AccessRequestIn, request: Request, session: SessionDep):
    if body.website:  # honeypot filled → a bot; pretend success
        return {"ok": True}
    contact_limiter.check(request)
    session.add(
        AccessRequest(
            name=body.name, email=str(body.email), company=body.company, message=body.message
        )
    )
    session.commit()
    await notify.notify_owner(
        f"New access request\n{body.name} <{body.email}>"
        + (f"\nCompany: {body.company}" if body.company else "")
        + (f"\n\n{body.message}" if body.message else "")
    )
    return {"ok": True}


@router.get("/meta")
def meta():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "contact_email": settings.contact_email,
        "contact_telegram": settings.contact_telegram,
        "check_interval_hours": settings.check_interval_hours,
        "features": {
            "ai": settings.llm_configured,
            "search": settings.search_configured,
            "telegram": settings.telegram_configured,
            "email": settings.email_configured,
        },
    }


@router.get("/health")
def health(session: SessionDep):
    """One place to see what works: database, background loops, configured services."""
    settings = get_settings()
    try:
        session.exec(text("SELECT 1"))
        db = "ok"
    except Exception as exc:
        db = f"error: {exc}"
    return {
        "status": "ok" if db == "ok" else "degraded",
        "database": db,
        "scheduler": {
            "status": scheduler.status,
            "last_tick": scheduler.last_tick,
            "running_checks": len(scheduler.active),
        },
        "telegram": {
            "configured": settings.telegram_configured,
            "poller": poller.status,
            "last_error": poller.last_error,
        },
        "ai": settings.llm_configured,
        "search": settings.search_configured,
        "email": settings.email_configured,
        "models": {"fast": settings.model_fast, "smart": settings.model_smart},
    }
