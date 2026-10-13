"""Response/request shapes of the HTTP API (mirrored in frontend/src/lib/types.ts)."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class SnapshotOut(BaseModel):
    id: int
    price: float
    currency: str
    in_stock: bool | None
    method: str
    fetched_via: str
    evidence: str
    flagged: bool
    flag_reason: str | None
    captured_at: datetime
    run_id: int | None


class OfferOut(BaseModel):
    id: int
    is_own: bool
    store: str
    domain: str
    url: str
    status: str
    source: str
    match_confidence: float | None
    match_reason: str | None
    title: str | None
    last_price: float | None
    currency: str | None
    in_stock: bool | None
    last_checked_at: datetime | None
    next_check_at: datetime | None
    fail_count: int
    last_error: str | None
    needs_review: bool
    latest: SnapshotOut | None = None


class PositionOut(BaseModel):
    own_price: float | None
    lowest: float | None
    median: float | None
    competitors: int
    diff_vs_lowest_pct: float | None
    label: str


class TrendPoint(BaseModel):
    day: str
    lowest: float | None
    own: float | None


class ProductSummary(BaseModel):
    id: int
    name: str
    brand: str | None
    image_url: str | None
    currency: str | None
    position: PositionOut
    lowest_store: str | None
    tracking: int
    proposed: int
    attention: int  # pages failing or readings waiting for review
    last_checked_at: datetime | None
    trend: list[TrendPoint]


class AlertOut(BaseModel):
    id: int
    product_id: int | None
    run_id: int | None
    kind: str
    title: str
    message: str
    links: list[dict[str, str]]
    read: bool
    delivered: list[str]
    created_at: datetime


class RunOut(BaseModel):
    id: int
    kind: str
    title: str
    status: str
    summary: str | None
    error: str | None
    product_id: int | None
    product_name: str | None
    tokens_in: int
    tokens_out: int
    cost_usd: float
    started_at: datetime
    finished_at: datetime | None


class ProductDetail(BaseModel):
    id: int
    name: str
    brand: str | None
    mpn: str | None
    gtin: str | None
    image_url: str | None
    currency: str | None
    market: str | None
    created_at: datetime
    position: PositionOut
    offers: list[OfferOut]
    alerts: list[AlertOut]
    runs: list[RunOut]


class HistorySeries(BaseModel):
    offer_id: int
    store: str
    is_own: bool
    currency: str | None
    points: list[dict[str, Any]]  # {t, price, flagged}


class EventOut(BaseModel):
    seq: int
    ts: datetime
    step: str
    level: str
    message: str
    data: dict[str, Any] | None


class RunStarted(BaseModel):
    run_id: int


class UrlIn(BaseModel):
    url: str = Field(min_length=4, max_length=2000)


class OfferUpdate(BaseModel):
    status: Literal["tracking", "rejected", "paused"]


class ReviewDecision(BaseModel):
    accept: bool


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class NotificationSettings(BaseModel):
    notify_email: bool
    alert_email: EmailStr | None = None
    notify_telegram: bool


class AccessRequestIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    company: str | None = Field(default=None, max_length=200)
    message: str = Field(default="", max_length=2000)
    website: str = ""  # honeypot: humans never see this field, bots fill it
