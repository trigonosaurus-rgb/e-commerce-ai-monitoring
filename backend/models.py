"""Database tables.

Ownership chain: User → Product → Offer → PriceSnapshot.
Your own product page is an Offer too (`is_own=True`), so your price gets the same
history, evidence and checks as competitor prices.
Every agent/scheduler action is a Run with an ordered list of RunEvents — that is what
the "Agent activity" screen shows.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, TypeDecorator
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Stores naive UTC in SQLite and always returns timezone-aware UTC datetimes,
    so the API serializes them with an explicit offset (no local-time confusion)."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is not None and value.tzinfo is not None:
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime | None, dialect):
        return value.replace(tzinfo=UTC) if value is not None else None


def _created() -> Any:
    return Field(default_factory=utcnow, sa_type=UTCDateTime)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str = ""
    is_demo: bool = False
    created_at: datetime = _created()
    # notification preferences
    notify_email: bool = False
    alert_email: str | None = None  # falls back to `email`
    notify_telegram: bool = False
    telegram_chat_id: str | None = None
    telegram_link_token: str | None = Field(default=None, index=True)


class UserSession(SQLModel, table=True):
    token_hash: str = Field(primary_key=True)  # sha256 of the cookie value
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = _created()
    expires_at: datetime = Field(sa_type=UTCDateTime)


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    brand: str | None = None
    mpn: str | None = None  # manufacturer part number / model
    gtin: str | None = None  # EAN/UPC — the most reliable way to match the same product
    image_url: str | None = None
    currency: str | None = None
    market: str | None = None  # country used for search, e.g. "germany"
    created_at: datetime = _created()


class Offer(SQLModel, table=True):
    """One product page in one store (yours or a competitor's)."""

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    is_own: bool = False
    store: str
    domain: str
    url: str
    status: str = "proposed"  # proposed | tracking | rejected | paused
    source: str = "agent"  # agent | manual
    match_confidence: float | None = None
    match_reason: str | None = None
    title: str | None = None  # product title as shown in that store
    last_price: float | None = None
    currency: str | None = None
    in_stock: bool | None = None
    last_checked_at: datetime | None = Field(default=None, sa_type=UTCDateTime)
    next_check_at: datetime | None = Field(default=None, sa_type=UTCDateTime, index=True)
    fail_count: int = 0
    last_error: str | None = None
    needs_review: bool = False  # last reading looked suspicious and was not trusted
    created_at: datetime = _created()


class PriceSnapshot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    offer_id: int = Field(foreign_key="offer.id", index=True)
    run_id: int | None = Field(default=None, foreign_key="run.id")
    price: float
    currency: str
    in_stock: bool | None = None
    method: str  # jsonld | microdata | meta | llm — how the price was read
    fetched_via: str  # direct | tavily — how the page was downloaded
    evidence: str  # the exact fragment the price came from
    flagged: bool = False
    flag_reason: str | None = None
    captured_at: datetime = _created()


class Run(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    product_id: int | None = Field(default=None, foreign_key="product.id", index=True)
    kind: str  # discovery | check
    title: str
    status: str = "running"  # running | completed | failed | interrupted
    summary: str | None = None
    error: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    started_at: datetime = _created()
    finished_at: datetime | None = Field(default=None, sa_type=UTCDateTime)


class RunEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", index=True)
    seq: int
    ts: datetime = _created()
    step: str
    level: str = "info"  # info | success | warning | error
    message: str
    data: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class Alert(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    product_id: int | None = Field(default=None, foreign_key="product.id", index=True)
    run_id: int | None = Field(default=None, foreign_key="run.id")
    kind: str  # price_drop | price_increase | undercut | stock | needs_review
    title: str
    message: str
    links: list[dict[str, str]] = Field(default_factory=list, sa_column=Column(JSON))
    read: bool = False
    delivered: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = _created()


class AccessRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    company: str | None = None
    message: str = ""
    created_at: datetime = _created()
