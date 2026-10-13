import uuid
from datetime import timedelta

import pytest
from sqlmodel import select

from backend import monitor
from backend.events import RunLogger
from backend.extraction import ProductData
from backend.fetching import FetchError
from backend.models import Alert, Offer, PriceSnapshot, Product, Run, utcnow
from backend.monitor import (
    OfferChange,
    Reading,
    alert_kind,
    is_significant,
    market_position,
    review_reason,
)
from backend.tests.conftest import make_user, session_scope


def reading(price: float, currency: str = "EUR") -> Reading:
    return Reading(
        price=price,
        currency=currency,
        in_stock=True,
        method="jsonld",
        via="direct",
        evidence=f'{{"price": "{price}"}}',
        title="Headphones",
        page_url="https://x",
    )


# ------------------------------------------------------------------ pure logic


def test_market_position_labels():
    assert market_position(90, [100, 120]).label == "cheapest"
    assert market_position(103, [100, 120]).label == "competitive"
    above = market_position(120, [100, 110, 130])
    assert (above.label, above.diff_vs_lowest_pct, above.median) == ("above_market", 20.0, 110)
    assert market_position(None, [100]).label == "no_data"
    assert market_position(100, []).label == "no_data"


def test_suspicious_readings_need_review():
    assert review_reason(100, "EUR", reading(30), 60) == "price moved -70% in one check"
    assert "currency" in review_reason(100, "EUR", reading(100, "USD"), 60)
    assert review_reason(100, "EUR", reading(95), 60) is None
    assert review_reason(None, None, reading(5), 60) is None  # first reading


def change(store="rival.de", old=100.0, new=90.0, own=False, **kw) -> OfferChange:
    return OfferChange(
        offer_id=1,
        store=store,
        url="https://rival.de/p",
        is_own=own,
        currency="EUR",
        old_price=old,
        new_price=new,
        old_in_stock=True,
        new_in_stock=True,
        **kw,
    )


def test_significance_threshold_and_own_price():
    assert is_significant(change(new=98.0), 1.0)
    assert not is_significant(change(new=99.5), 1.0)  # −0.5% is just noise
    assert not is_significant(change(own=True, new=50.0), 1.0)
    assert is_significant(change(new=99.9, suspicious="price moved"), 1.0)


def test_alert_kind_detects_undercut():
    before = market_position(95, [100])
    after = market_position(95, [90])
    assert alert_kind([change(new=90.0)], before, after) == "undercut"
    assert (
        alert_kind(
            [change(old=120, new=110)],
            market_position(95, [100, 120]),
            market_position(95, [100, 110]),
        )
        == "price_drop"
    )


# --------------------------------------------------------- check with a fake page


@pytest.fixture
def tracked_product():
    user = make_user()
    page = uuid.uuid4().hex[:8]  # unique pages: a reading is shared between offers of one URL
    with session_scope() as session:
        product = Product(user_id=user.id, name="Sony WH-1000XM6", currency="EUR")
        session.add(product)
        session.flush()
        own = Offer(
            product_id=product.id,
            is_own=True,
            store="me.de",
            domain="me.de",
            url=f"https://me.de/{page}",
            status="tracking",
            last_price=95.0,
            currency="EUR",
        )
        rival = Offer(
            product_id=product.id,
            store="rival.de",
            domain="rival.de",
            url=f"https://rival.de/{page}",
            status="tracking",
            last_price=100.0,
            currency="EUR",
            next_check_at=utcnow() - timedelta(minutes=1),
        )
        session.add_all([own, rival])
        session.commit()
        return user, product, own, rival


@pytest.mark.anyio
async def test_check_records_evidence_and_alerts_on_undercut(monkeypatch, tracked_product):
    user, product, own, rival = tracked_product
    prices = {own.url: 95.0, rival.url: 89.0}

    async def fake_read_price(url, usage):
        return reading(prices[url]), ProductData()

    monkeypatch.setattr(monitor, "read_price", fake_read_price)
    run = RunLogger.start(user_id=user.id, kind="check", title="test", product_id=product.id)
    summary = await monitor.check_product(product.id, run)

    assert summary.startswith("2/2 pages read · 1 notable change")
    with session_scope() as session:
        snaps = session.exec(select(PriceSnapshot).where(PriceSnapshot.offer_id == rival.id)).all()
        alert = session.exec(select(Alert).where(Alert.product_id == product.id)).one()
        updated = session.get(Offer, rival.id)
    assert [s.price for s in snaps] == [89.0] and snaps[0].evidence
    assert updated.last_price == 89.0 and updated.next_check_at > utcnow()
    assert alert.kind == "undercut"
    assert "rival.de" in alert.message and "-11.0%" in alert.message  # template, no LLM in tests
    assert alert.links == [{"label": "rival.de", "url": rival.url}]


@pytest.mark.anyio
async def test_implausible_jump_is_kept_for_review(monkeypatch, tracked_product):
    user, product, _own, rival = tracked_product

    async def fake_read_price(url, usage):
        return reading(9.99), ProductData()  # −90%: probably an accessory or a parsing issue

    monkeypatch.setattr(monitor, "read_price", fake_read_price)
    run = RunLogger.start(user_id=user.id, kind="check", title="test", product_id=product.id)
    await monitor.check_product(product.id, run, [rival.id])

    with session_scope() as session:
        offer = session.get(Offer, rival.id)
        snap = session.exec(select(PriceSnapshot).where(PriceSnapshot.offer_id == rival.id)).one()
        alert = session.exec(select(Alert).where(Alert.product_id == product.id)).one()
    assert offer.last_price == 100.0 and offer.needs_review  # old trusted price is kept
    assert snap.flagged and "-90%" in snap.flag_reason
    assert alert.kind == "needs_review"


@pytest.mark.anyio
async def test_failed_page_backs_off_and_keeps_going(monkeypatch, tracked_product):
    user, product, own, rival = tracked_product

    async def fake_read_price(url, usage):
        if url == rival.url:
            raise FetchError("Couldn't load the page: HTTP 403.")
        return reading(95.0), ProductData()

    monkeypatch.setattr(monitor, "read_price", fake_read_price)
    run = RunLogger.start(user_id=user.id, kind="check", title="test", product_id=product.id)
    summary = await monitor.check_product(product.id, run)

    with session_scope() as session:
        offer = session.get(Offer, rival.id)
        run_row = session.get(Run, run.run_id)
    assert summary.endswith("1 page(s) failed")
    assert offer.fail_count == 1 and "403" in offer.last_error
    assert timedelta(minutes=25) < offer.next_check_at - utcnow() < timedelta(minutes=35)
    assert run_row.status == "running"  # finishing the run is the scheduler's job


@pytest.mark.anyio
async def test_same_page_in_another_workspace_is_read_once(monkeypatch, tracked_product):
    user, product, _own, rival = tracked_product
    other = make_user()
    with session_scope() as session:
        copy = Product(user_id=other.id, name="Sony WH-1000XM6", currency="EUR")
        session.add(copy)
        session.flush()
        twin = Offer(
            product_id=copy.id,
            store="rival.de",
            domain="rival.de",
            url=rival.url,
            status="tracking",
            last_price=100.0,
            currency="EUR",
        )
        session.add(twin)
        session.commit()
        copy_id, twin_id = copy.id, twin.id
    downloads = []

    async def fake_read_price(url, usage):
        downloads.append(url)
        return reading(97.0), ProductData()

    monkeypatch.setattr(monitor, "read_price", fake_read_price)
    first = RunLogger.start(user_id=user.id, kind="check", title="t", product_id=product.id)
    await monitor.check_product(product.id, first, [rival.id])
    second = RunLogger.start(user_id=other.id, kind="check", title="t", product_id=copy_id)
    await monitor.check_product(copy_id, second, [twin_id])

    assert downloads == [rival.url]
    with session_scope() as session:
        snap = session.exec(select(PriceSnapshot).where(PriceSnapshot.offer_id == twin_id)).one()
        assert snap.price == 97.0 and snap.run_id == second.run_id
        assert session.get(Offer, twin_id).last_price == 97.0
