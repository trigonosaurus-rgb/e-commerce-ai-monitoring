"""Test setup: a throw-away SQLite database, no background loops, no external services.

Environment variables are set before `backend` is imported, and they take priority over
the developer's `.env`, so tests never call OpenAI, Tavily, Telegram or SMTP.
"""

import os
import tempfile
import uuid
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="rivalscope-tests-"))
os.environ.update(
    {
        "DATABASE_URL": f"sqlite:///{(_tmp / 'test.db').as_posix()}",
        "SCHEDULER_ENABLED": "false",
        "OPENAI_API_KEY": "",
        "TAVILY_API_KEY": "",
        "TELEGRAM_BOT_TOKEN": "",
        "SMTP_HOST": "",
        "BROWSER_FINGERPRINT": "false",  # no real network: tests use httpx fakes
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.auth import hash_password  # noqa: E402
from backend.database import init_db, session_scope  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import User  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
init_db()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def fixture_html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def make_user(password: str = "secret-pass") -> User:
    with session_scope() as session:
        user = User(
            email=f"user-{uuid.uuid4().hex[:8]}@example.com", password_hash=hash_password(password)
        )
        session.add(user)
        session.commit()
        return user


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user():
    return make_user()


@pytest.fixture
def logged_in(client, user):
    response = client.post("/api/auth/login", json={"email": user.email, "password": "secret-pass"})
    assert response.status_code == 200, response.text
    return client
