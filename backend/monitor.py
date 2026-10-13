"""Price checks: read each tracked page, store the reading with its evidence, raise alerts.

Flow of one check:  fetch page → read price (structured data, LLM fallback) →
sanity rules (currency, implausible jump) → PriceSnapshot → compare with the previous
price → market position computed in Python → alert text (LLM or template) → channels.
"""

import asyncio
import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import timedelta

from sqlmodel import select

from backend import llm, notify
from backend.config import get_settings
from backend.database import session_scope
from backend.events import RunLogger
from backend.extraction import ProductData, read_product_data
from backend.fetching import FetchError, fetch_page, fetch_via_tavily
from backend.models import Alert, Offer, PriceSnapshot, Product, utcnow

log = logging.getLogger(__name__)
METHOD_LABELS = {
    "jsonld": "structured data",
    "microdata": "structured data",
    "meta": "page meta tags",
    "llm": "AI reading, verified against page text",
}


class NoPriceError(FetchError):
    pass


def fmt_money(value: float | None, currency: str | None) -> str:
    return "—" if value is None else f"{value:,.2f} {currency or ''}".strip()


def pct_change(old: float, new: float) -> float:
    return (new - old) / old * 100


@dataclass
class Reading:
    price: float
    currency: str
    in_stock: bool | None
    method: str
    via: str
    evidence: str
    title: str | None
    page_url: str


async def read_price(url: str, usage: llm.UsageSink | None) -> tuple[Reading, ProductData]:
    page = await fetch_page(url)
    data = await read_product_data(page, usage=usage)
    if not data.has_price and page.via == "direct" and get_settings().search_configured:
        # second chance: the price may appear only after JavaScript runs
        if rendered := await fetch_via_tavily(url):
            second = await read_product_data(rendered, usage=usage)
            if second.has_price:
                for field in ("name", "brand", "mpn", "gtin", "condition"):
                    setattr(second, field, getattr(second, field) or getattr(data, field))
                page, data = rendered, second
    if not data.has_price:
        raise NoPriceError(data.note or "No price found on the page.")
    reading = Reading(
        price=data.price,
        currency=data.currency,
        in_stock=data.in_stock,
        method=data.method,
        via=page.via,
        evidence=data.evidence,
        title=data.name,
        page_url=page.url,
    )
    return reading, data


# ---------------------------------------------------------------- pure decision logic


@dataclass
class Position:
    own_price: float | None
    lowest: float | None
    median: float | None
    competitors: int
    diff_vs_lowest_pct: float | None  # +4.0 means you are 4% more expensive than the cheapest
    label: str  # cheapest | competitive | above_market | no_data


def market_position(own_price: float | None, competitor_prices: list[float]) -> Position:
    prices = sorted(p for p in competitor_prices if p)
    if own_price is None or not prices:
        return Position(
            own_price,
            prices[0] if prices else None,
            statistics.median(prices) if prices else None,
            len(prices),
            None,
            "no_data",
        )
    lowest = prices[0]
    diff = pct_change(lowest, own_price)
    label = "cheapest" if own_price <= lowest else "competitive" if diff <= 5 else "above_market"
    return Position(
        own_price, lowest, statistics.median(prices), len(prices), round(diff, 1), label
    )


def review_reason(
    last_price: float | None, last_currency: str | None, reading: Reading, jump_limit_pct: float
) -> str | None:
    """A reading we shouldn't trust blindly — kept as evidence, but needs a human look."""
    if last_currency and reading.currency != last_currency:
        return f"currency changed from {last_currency} to {reading.currency}"
    if last_price and abs(pct_change(last_price, reading.price)) > jump_limit_pct:
        return f"price moved {pct_change(last_price, reading.price):+.0f}% in one check"
    return None


@dataclass
class OfferChange:
    offer_id: int
    store: str
    url: str
    is_own: bool
    currency: str
    old_price: float | None
    new_price: float
    old_in_stock: bool | None
    new_in_stock: bool | None
    suspicious: str | None = None

    @property
    def pct(self) -> float | None:
        return None if not self.old_price else round(pct_change(self.old_price, self.new_price), 1)

    @property
    def stock_changed(self) -> bool:
        return (
            self.old_in_stock is not None
            and self.new_in_stock is not None
            and self.old_in_stock != self.new_in_stock
        )


def is_significant(change: OfferChange, min_pct: float) -> bool:
    if change.suspicious:
        return True
    if change.is_own:  # your own price moving is shown in history, not alerted
        return False
    return change.stock_changed or (change.pct is not None and abs(change.pct) >= min_pct)


def alert_kind(changes: list[OfferChange], before: Position, after: Position) -> str:
    competitor = [c for c in changes if not c.is_own and not c.suspicious]
    became_undercut = (
        after.own_price is not None
        and after.lowest is not None
        and after.lowest < after.own_price
        and (before.lowest is None or before.own_price is None or before.lowest >= before.own_price)
    )
    if competitor and became_undercut:
        return "undercut"
    if any(c.pct is not None and c.pct < 0 for c in competitor):
        return "price_drop"
    if any(c.pct is not None and c.pct > 0 for c in competitor):
        return "price_increase"
    if any(c.stock_changed for c in competitor):
        return "stock"
    return "needs_review"


def template_alert(
    product_name: str, changes: list[OfferChange], after: Position
) -> tuple[str, str]:
    lines = []
    for c in changes:
        if c.suspicious:
            lines.append(
                f"{c.store}: a reading of {fmt_money(c.new_price, c.currency)} looks "
                f"suspicious ({c.suspicious}) and was kept for your review."
            )
            continue
        if c.pct:
            lines.append(
                f"{c.store}: {fmt_money(c.old_price, c.currency)} → "
                f"{fmt_money(c.new_price, c.currency)} ({c.pct:+.1f}%)."
            )
        if c.stock_changed:
            lines.append(f"{c.store} is now {'in stock' if c.new_in_stock else 'out of stock'}.")
    if after.label == "cheapest":
        lines.append("You are still the cheapest offer.")
    elif after.diff_vs_lowest_pct is not None:
        lines.append(f"You are now {after.diff_vs_lowest_pct:.1f}% above the cheapest competitor.")
    first = changes[0]
    if len(changes) == 1 and first.pct and not first.suspicious:
        verb = "dropped" if first.pct < 0 else "raised"
        title = f"{first.store} {verb} the price by {abs(first.pct):.1f}% · {product_name}"
    else:
        title = f"{len(changes)} competitor updates · {product_name}"
    return title[:120], " ".join(lines)


# --------------------------------------------------------------------------- checks


def _backoff(fail_count: int) -> timedelta:
    interval = timedelta(hours=get_settings().check_interval_hours)
    return min(timedelta(minutes=30) * 2 ** max(fail_count - 1, 0), interval)


async def check_offer(offer_id: int, run: RunLogger) -> tuple[bool, OfferChange | None]:
    """Returns (success, change-or-None)."""
    settings = get_settings()
    with session_scope() as session:
        offer = session.get(Offer, offer_id)
    try:
        reading, _ = await read_price(offer.url, run)
    except (FetchError, llm.LLMError) as exc:
        with session_scope() as session:
            failed = session.get(Offer, offer_id)
            failed.fail_count += 1
            failed.last_error = str(exc)
            failed.last_checked_at = utcnow()
            failed.next_check_at = utcnow() + _backoff(failed.fail_count)
            session.commit()
        run.log("check", f"{offer.store}: {exc}", level="warning", url=offer.url, store=offer.store)
        return False, None

    suspicious = review_reason(offer.last_price, offer.currency, reading, settings.review_jump_pct)
    with session_scope() as session:
        current = session.get(Offer, offer_id)
        old_price, old_stock = current.last_price, current.in_stock
        session.add(
            PriceSnapshot(
                offer_id=offer_id,
                run_id=run.run_id,
                price=reading.price,
                currency=reading.currency,
                in_stock=reading.in_stock,
                method=reading.method,
                fetched_via=reading.via,
                evidence=reading.evidence,
                flagged=bool(suspicious),
                flag_reason=suspicious,
            )
        )
        current.last_checked_at = utcnow()
        current.next_check_at = utcnow() + timedelta(hours=settings.check_interval_hours)
        current.fail_count, current.last_error = 0, None
        current.title = current.title or reading.title
        if suspicious:
            current.needs_review = True
        else:
            current.last_price, current.currency = reading.price, reading.currency
            current.in_stock, current.needs_review = reading.in_stock, False
        session.commit()

    details = {
        "url": offer.url,
        "store": offer.store,
        "price": reading.price,
        "currency": reading.currency,
        "in_stock": reading.in_stock,
        "method": reading.method,
        "via": reading.via,
        "evidence": reading.evidence[:300],
    }
    if suspicious:
        run.log(
            "check",
            f"{offer.store}: read {fmt_money(reading.price, reading.currency)}, but "
            f"{suspicious} — kept for review instead of trusting it.",
            level="warning",
            **details,
        )
    else:
        run.log(
            "check",
            f"{offer.store}: {fmt_money(reading.price, reading.currency)} "
            f"(from {METHOD_LABELS.get(reading.method, reading.method)})",
            level="success",
            **details,
        )

    change = OfferChange(
        offer_id=offer_id,
        store=offer.store,
        url=offer.url,
        is_own=offer.is_own,
        currency=reading.currency,
        old_price=old_price,
        new_price=reading.price,
        old_in_stock=old_stock,
        new_in_stock=reading.in_stock,
        suspicious=suspicious,
    )
    changed = old_price is not None and old_price != reading.price
    return True, change if (suspicious or changed or change.stock_changed) else None


def current_position(product_id: int) -> Position:
    with session_scope() as session:
        offers = session.exec(
            select(Offer).where(Offer.product_id == product_id, Offer.status == "tracking")
        ).all()
    own = next((o.last_price for o in offers if o.is_own), None)
    own_currency = next((o.currency for o in offers if o.is_own), None)
    competitors = [
        o.last_price
        for o in offers
        if not o.is_own and o.last_price and (own_currency is None or o.currency == own_currency)
    ]
    return market_position(own, competitors)


async def check_product(product_id: int, run: RunLogger, offer_ids: list[int] | None = None) -> str:
    settings = get_settings()
    with session_scope() as session:
        product = session.get(Product, product_id)
        query = select(Offer).where(Offer.product_id == product_id, Offer.status == "tracking")
        if offer_ids:
            query = query.where(Offer.id.in_(offer_ids))
        offers = session.exec(query).all()
    if not offers:
        run.log("plan", "Nothing to check — no tracked pages.", level="warning")
        return "No tracked pages"

    before = current_position(product_id)
    run.log(
        "plan",
        f"Checking {len(offers)} page(s) for {product.name}",
        pages=[{"store": o.store, "url": o.url} for o in offers],
    )
    limit = asyncio.Semaphore(4)

    async def guarded(offer_id: int):
        async with limit:
            return await check_offer(offer_id, run)

    results = await asyncio.gather(*(guarded(o.id) for o in offers))
    ok = sum(1 for success, _ in results if success)
    changes = [c for _, c in results if c is not None]
    after = current_position(product_id)
    significant = [c for c in changes if is_significant(c, settings.alert_min_change_pct)]
    if significant:
        await create_alert(product, significant, before, after, run)
    elif changes:
        run.log("compare", "Small changes only — below the alert threshold.")
    else:
        run.log("compare", "No price or stock changes.")

    summary = f"{ok}/{len(offers)} pages read · {len(significant)} notable change(s)"
    failed = len(offers) - ok
    return summary + (f" · {failed} page(s) failed" if failed else "")


async def create_alert(
    product: Product, changes: list[OfferChange], before: Position, after: Position, run: RunLogger
) -> None:
    kind = alert_kind(changes, before, after)
    title, message = template_alert(product.name, changes, after)
    if get_settings().llm_configured:
        facts = {
            "product": product.name,
            "alert_type": kind,
            "changes": [
                {k: v for k, v in asdict(c).items() if k not in ("offer_id", "url")}
                | {"change_pct": c.pct}
                for c in changes
            ],
            "position_before": asdict(before),
            "position_now": asdict(after),
        }
        try:
            insight = await llm.write_insight(facts, usage=run)
            title, message = insight.title[:120], insight.message
        except llm.LLMError as exc:
            run.log(
                "alert",
                f"AI summary unavailable, using the plain template ({exc})",
                level="warning",
            )
    links = [{"label": c.store, "url": c.url} for c in changes]
    with session_scope() as session:
        alert = Alert(
            user_id=product.user_id,
            product_id=product.id,
            run_id=run.run_id,
            kind=kind,
            title=title,
            message=message,
            links=links,
        )
        session.add(alert)
        session.commit()
        alert_id = alert.id
    run.log(
        "alert",
        f"Alert created: {title}",
        level="success",
        alert_id=alert_id,
        kind=kind,
        text=message,
    )
    await notify.dispatch(alert_id)
