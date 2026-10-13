"""Products, competitor offers, price history and the dashboard."""

from collections import defaultdict
from dataclasses import asdict
from datetime import timedelta

from fastapi import APIRouter
from sqlmodel import Session, col, func, select

from backend import search
from backend.agent.discovery import run_discovery
from backend.api.schemas import (
    AlertOut,
    HistorySeries,
    OfferOut,
    OfferUpdate,
    PositionOut,
    ProductDetail,
    ProductSummary,
    ReviewDecision,
    RunOut,
    RunStarted,
    SnapshotOut,
    TrendPoint,
    UrlIn,
)
from backend.auth import Workspace, WorkspaceDep, api_error
from backend.config import get_settings
from backend.database import SessionDep
from backend.events import RunLogger, spawn
from backend.fetching import FetchError, ensure_public_url, normalize_url
from backend.models import Alert, Offer, PriceSnapshot, Product, Run, utcnow
from backend.monitor import current_position
from backend.scheduler import CheckAlreadyRunning, scheduler

router = APIRouter(tags=["products"])


# ------------------------------------------------------------------------- helpers


def owned_product(session: Session, ws: Workspace, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if product is None or product.user_id != ws.user.id:
        raise api_error(404, "not_found", "Product not found.")
    return product


def owned_offer(session: Session, ws: Workspace, offer_id: int) -> Offer:
    offer = session.get(Offer, offer_id)
    if offer is None:
        raise api_error(404, "not_found", "Offer not found.")
    owned_product(session, ws, offer.product_id)
    return offer


async def checked_url(raw: str) -> str:
    url = normalize_url(raw)
    try:
        await ensure_public_url(url)
    except FetchError as exc:
        raise api_error(400, "bad_url", str(exc)) from exc
    return url


def offer_out(session: Session, offer: Offer) -> OfferOut:
    latest = session.exec(
        select(PriceSnapshot)
        .where(PriceSnapshot.offer_id == offer.id)
        .order_by(col(PriceSnapshot.captured_at).desc())
        .limit(1)
    ).first()
    out = OfferOut.model_validate(offer, from_attributes=True)
    out.latest = SnapshotOut.model_validate(latest, from_attributes=True) if latest else None
    return out


def run_out(run: Run, product_name: str | None) -> RunOut:
    return RunOut.model_validate(run.model_dump() | {"product_name": product_name})


def _trend(session: Session, offers: list[Offer], days: int = 14) -> list[TrendPoint]:
    since = utcnow() - timedelta(days=days)
    ids = {o.id: o for o in offers if o.status == "tracking"}
    if not ids:
        return []
    rows = session.exec(
        select(PriceSnapshot).where(
            col(PriceSnapshot.offer_id).in_(ids),
            PriceSnapshot.captured_at >= since,
            col(PriceSnapshot.flagged).is_(False),
        )
    ).all()
    lowest: dict[str, float] = {}
    own: dict[str, float] = {}
    for snap in rows:
        day = snap.captured_at.date().isoformat()
        target = own if ids[snap.offer_id].is_own else lowest
        target[day] = min(target.get(day, snap.price), snap.price)
    return [
        TrendPoint(day=d, lowest=lowest.get(d), own=own.get(d))
        for d in sorted(set(lowest) | set(own))
    ]


# ------------------------------------------------------------------------ products


@router.get("/products", response_model=list[ProductSummary])
def list_products(ws: WorkspaceDep, session: SessionDep):
    products = session.exec(
        select(Product)
        .where(Product.user_id == ws.user.id)
        .order_by(col(Product.created_at).desc())
    ).all()
    result = []
    for p in products:
        offers = session.exec(select(Offer).where(Offer.product_id == p.id)).all()
        tracking = [o for o in offers if o.status == "tracking"]
        position = current_position(p.id)
        cheapest = min(
            (o for o in tracking if not o.is_own and o.last_price),
            key=lambda o: o.last_price,
            default=None,
        )
        checked = [o.last_checked_at for o in tracking if o.last_checked_at]
        result.append(
            ProductSummary(
                id=p.id,
                name=p.name,
                brand=p.brand,
                image_url=p.image_url,
                currency=p.currency,
                position=PositionOut(**asdict(position)),
                lowest_store=cheapest.store if cheapest else None,
                tracking=sum(1 for o in tracking if not o.is_own),
                proposed=sum(1 for o in offers if o.status == "proposed"),
                attention=sum(1 for o in tracking if o.fail_count or o.needs_review),
                last_checked_at=max(checked) if checked else None,
                trend=_trend(session, offers),
            )
        )
    return result


@router.post("/products", response_model=RunStarted, status_code=202)
async def add_product(body: UrlIn, ws: WorkspaceDep, session: SessionDep):
    ws.require_write()
    settings = get_settings()
    if not (settings.llm_configured and settings.search_configured):
        raise api_error(
            503,
            "not_configured",
            "The AI agent needs OPENAI_API_KEY and TAVILY_API_KEY on the server.",
        )
    count = session.exec(select(func.count()).where(Product.user_id == ws.user.id)).one()
    if count >= settings.max_products_per_user:
        raise api_error(
            409, "limit_reached", f"Your plan allows {settings.max_products_per_user} products."
        )
    url = await checked_url(body.url)
    run = RunLogger.start(
        user_id=ws.user.id, kind="discovery", title=f"Find competitors · {search.domain_of(url)}"
    )
    spawn(run_discovery(run, url=url), name=f"discovery-{run.run_id}")
    return RunStarted(run_id=run.run_id)


@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, ws: WorkspaceDep, session: SessionDep):
    p = owned_product(session, ws, product_id)
    offers = session.exec(
        select(Offer)
        .where(Offer.product_id == p.id)
        .order_by(col(Offer.is_own).desc(), col(Offer.last_price))
    ).all()
    alerts = session.exec(
        select(Alert)
        .where(Alert.product_id == p.id)
        .order_by(col(Alert.created_at).desc())
        .limit(5)
    ).all()
    runs = session.exec(
        select(Run).where(Run.product_id == p.id).order_by(col(Run.started_at).desc()).limit(8)
    ).all()
    return ProductDetail(
        **p.model_dump(),
        position=PositionOut(**asdict(current_position(p.id))),
        offers=[offer_out(session, o) for o in offers if o.status != "rejected"],
        alerts=[AlertOut.model_validate(a, from_attributes=True) for a in alerts],
        runs=[run_out(r, p.name) for r in runs],
    )


@router.get("/products/{product_id}/history", response_model=list[HistorySeries])
def product_history(product_id: int, ws: WorkspaceDep, session: SessionDep, days: int = 90):
    owned_product(session, ws, product_id)
    since = utcnow() - timedelta(days=days)
    offers = session.exec(
        select(Offer).where(
            Offer.product_id == product_id, col(Offer.status).in_(["tracking", "paused"])
        )
    ).all()
    snaps = session.exec(
        select(PriceSnapshot)
        .where(
            col(PriceSnapshot.offer_id).in_([o.id for o in offers]),
            PriceSnapshot.captured_at >= since,
        )
        .order_by(col(PriceSnapshot.captured_at))
    ).all()
    points: dict[int, list] = defaultdict(list)
    for s in snaps:
        points[s.offer_id].append(
            {
                "t": s.captured_at.isoformat(),
                "price": s.price,
                "flagged": s.flagged,
                "snapshot_id": s.id,
            }
        )
    return [
        HistorySeries(
            offer_id=o.id, store=o.store, is_own=o.is_own, currency=o.currency, points=points[o.id]
        )
        for o in offers
    ]


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, ws: WorkspaceDep, session: SessionDep):
    ws.require_write()
    product = owned_product(session, ws, product_id)
    if product_id in scheduler.active:
        raise api_error(409, "busy", "A check is running for this product. Try again in a minute.")
    offer_ids = [o.id for o in session.exec(select(Offer).where(Offer.product_id == product_id))]
    for snap in session.exec(
        select(PriceSnapshot).where(col(PriceSnapshot.offer_id).in_(offer_ids))
    ):
        session.delete(snap)
    for alert in session.exec(select(Alert).where(Alert.product_id == product_id)):
        session.delete(alert)
    for run in session.exec(select(Run).where(Run.product_id == product_id)):
        run.product_id = None  # keep the agent history, just unlink it
    session.flush()
    for offer in session.exec(select(Offer).where(Offer.product_id == product_id)):
        session.delete(offer)
    session.flush()
    session.delete(product)
    session.commit()


@router.post("/products/{product_id}/discover", response_model=RunStarted, status_code=202)
async def discover_more(product_id: int, ws: WorkspaceDep, session: SessionDep):
    ws.require_write()
    product = owned_product(session, ws, product_id)
    run = RunLogger.start(
        user_id=ws.user.id,
        kind="discovery",
        product_id=product.id,
        title=f"Find more competitors · {product.name}",
    )
    spawn(run_discovery(run, product_id=product.id), name=f"discovery-{run.run_id}")
    return RunStarted(run_id=run.run_id)


@router.post("/products/{product_id}/check", response_model=RunStarted, status_code=202)
async def check_now(product_id: int, ws: WorkspaceDep, session: SessionDep):
    ws.require_write()
    owned_product(session, ws, product_id)
    try:
        run = scheduler.begin(product_id, "Manual check")
    except CheckAlreadyRunning as exc:
        raise api_error(409, "busy", str(exc)) from exc
    spawn(scheduler.execute(run, product_id), name=f"check-{run.run_id}")
    return RunStarted(run_id=run.run_id)


@router.post("/products/{product_id}/offers", response_model=OfferOut, status_code=201)
async def add_offer(product_id: int, body: UrlIn, ws: WorkspaceDep, session: SessionDep):
    """Track a competitor page you already know (no AI search needed)."""
    ws.require_write()
    owned_product(session, ws, product_id)
    url = await checked_url(body.url)
    existing = session.exec(select(Offer).where(Offer.product_id == product_id)).all()
    if any(o.url == url for o in existing):
        raise api_error(409, "duplicate", "This page is already on the list.")
    active = [o for o in existing if not o.is_own and o.status != "rejected"]
    if len(active) >= get_settings().max_offers_per_product:
        raise api_error(
            409, "limit_reached", "This product already has the maximum number of competitor pages."
        )
    domain = search.domain_of(url)
    offer = Offer(
        product_id=product_id,
        store=domain,
        domain=domain,
        url=url,
        status="tracking",
        source="manual",
        next_check_at=utcnow(),
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    try:  # read the price right away; if busy, the scheduler picks it up within a minute
        run = scheduler.begin(product_id, "First check")
        spawn(scheduler.execute(run, product_id, [offer.id]), name=f"check-{run.run_id}")
    except CheckAlreadyRunning:
        pass
    return offer_out(session, offer)


# -------------------------------------------------------------------------- offers


@router.patch("/offers/{offer_id}", response_model=OfferOut)
def update_offer(offer_id: int, body: OfferUpdate, ws: WorkspaceDep, session: SessionDep):
    """Approve (tracking), reject or pause a competitor page."""
    ws.require_write()
    offer = owned_offer(session, ws, offer_id)
    if offer.is_own and body.status == "rejected":
        raise api_error(400, "bad_request", "Your own page can be paused, not rejected.")
    if body.status == "tracking" and offer.status != "tracking":
        offer.next_check_at = utcnow() + timedelta(hours=get_settings().check_interval_hours)
        if offer.status == "paused":
            offer.next_check_at = utcnow()
    offer.status = body.status
    session.commit()
    session.refresh(offer)
    return offer_out(session, offer)


@router.post("/offers/{offer_id}/review", response_model=OfferOut)
def review_reading(offer_id: int, body: ReviewDecision, ws: WorkspaceDep, session: SessionDep):
    """Accept or dismiss a suspicious price reading."""
    ws.require_write()
    offer = owned_offer(session, ws, offer_id)
    latest = session.exec(
        select(PriceSnapshot)
        .where(PriceSnapshot.offer_id == offer.id)
        .order_by(col(PriceSnapshot.captured_at).desc())
        .limit(1)
    ).first()
    if body.accept and latest is not None:
        latest.flagged, latest.flag_reason = False, f"accepted by user ({latest.flag_reason})"
        offer.last_price, offer.currency, offer.in_stock = (
            latest.price,
            latest.currency,
            latest.in_stock,
        )
    offer.needs_review = False
    session.commit()
    session.refresh(offer)
    return offer_out(session, offer)


@router.get("/offers/{offer_id}/snapshots", response_model=list[SnapshotOut])
def offer_snapshots(offer_id: int, ws: WorkspaceDep, session: SessionDep, limit: int = 100):
    owned_offer(session, ws, offer_id)
    return session.exec(
        select(PriceSnapshot)
        .where(PriceSnapshot.offer_id == offer_id)
        .order_by(col(PriceSnapshot.captured_at).desc())
        .limit(min(limit, 500))
    ).all()


# ----------------------------------------------------------------------- dashboard


@router.get("/dashboard")
def dashboard(ws: WorkspaceDep, session: SessionDep):
    uid = ws.user.id
    week = utcnow() - timedelta(days=7)
    month = utcnow() - timedelta(days=30)
    product_ids = list(session.exec(select(Product.id).where(Product.user_id == uid)))
    offers = session.exec(select(Offer).where(col(Offer.product_id).in_(product_ids))).all()
    labels: dict[str, int] = defaultdict(int)
    for pid in product_ids:
        labels[current_position(pid).label] += 1
    runs = session.exec(select(Run).where(Run.user_id == uid, Run.started_at >= month)).all()
    checked = [o.last_checked_at for o in offers if o.last_checked_at]
    return {
        "products": len(product_ids),
        "competitors": sum(1 for o in offers if not o.is_own and o.status == "tracking"),
        "proposed": sum(1 for o in offers if o.status == "proposed"),
        "attention": sum(
            1 for o in offers if o.status == "tracking" and (o.fail_count or o.needs_review)
        ),
        "alerts_7d": session.exec(
            select(func.count()).where(Alert.user_id == uid, Alert.created_at >= week)
        ).one(),
        "unread_alerts": session.exec(
            select(func.count()).where(Alert.user_id == uid, col(Alert.read).is_(False))
        ).one(),
        "checks_7d": sum(1 for r in runs if r.kind == "check" and r.started_at >= week),
        "cost_30d_usd": round(sum(r.cost_usd for r in runs), 4),
        "positions": dict(labels),
        "last_check_at": max(checked) if checked else None,
    }
