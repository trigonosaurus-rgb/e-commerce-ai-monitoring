"""The discovery graph with fake web, search and LLM — checks the agent's decisions."""

import pytest
from sqlmodel import col, select

from backend import llm, search
from backend.agent import discovery
from backend.events import RunLogger
from backend.extraction import ProductData
from backend.fetching import FetchError, Page
from backend.models import Offer, Product, Run, RunEvent
from backend.monitor import Reading
from backend.search import SearchResult
from backend.tests.conftest import make_user, session_scope

OURS = ProductData(name="Sony WH-1000XM6", brand="Sony", gtin="4548736160213", price=399.0,
                   currency="EUR", in_stock=True, method="jsonld", evidence='{"price":"399"}')

# what each competitor page "contains"
PAGES = {
    "https://good-one.de/xm6": ProductData(name="Sony WH-1000XM6 black", gtin="04548736160213"),
    "https://other-model.de/xm5": ProductData(name="Sony WH-1000XM5", gtin="4548736132586"),
    "https://good-two.de/sony-xm6": ProductData(name="WH-1000XM6"),
}
PRICES = {"https://good-one.de/xm6": 379.0, "https://other-model.de/xm5": 279.0,
          "https://good-two.de/sony-xm6": 389.0}


def result(url: str, title: str) -> SearchResult:
    return SearchResult(url=url, title=title, snippet=title, domain=search.domain_of(url))


@pytest.fixture
def fake_world(monkeypatch):
    calls = {"plan": 0}

    async def fake_fetch(url, client=None):
        return Page(url=url, text="our page", html="<html></html>", via="direct")

    async def fake_read_product_data(page, usage=None):
        return OURS

    async def fake_read_price(url, usage):
        if url == "https://blocked.de/xm6":
            raise FetchError("Couldn't load the page: HTTP 403.")
        reading = Reading(price=PRICES[url], currency="EUR", in_stock=True, method="jsonld",
                          via="direct", evidence=f'{{"price": "{PRICES[url]}"}}',
                          title=PAGES[url].name, page_url=url)
        return reading, PAGES[url]

    async def fake_plan(product, *, store_url, previous, feedback, usage):
        calls["plan"] += 1
        return llm.SearchPlan(market_country="germany", queries=[f"sony xm6 kaufen {calls['plan']}"])

    async def fake_search(query, *, country=None, exclude_domains=None, max_results=8):
        assert country == "germany" and "my-shop.de" in exclude_domains
        if query.endswith("1"):
            return [result("https://good-one.de/xm6", "Sony WH-1000XM6"),
                    result("https://other-model.de/xm5", "Sony WH-1000XM5"),
                    result("https://blog.de/review", "XM6 review"),
                    result("https://blocked.de/xm6", "Sony WH-1000XM6")]
        if query == "4548736160213":
            return []
        return [result("https://good-two.de/sony-xm6", "WH-1000XM6 kaufen")]

    async def fake_judge(product, candidates, *, usage):
        verdicts = []
        for i, c in enumerate(candidates):
            verdict = "not_a_store_page" if "blog" in c["url"] else "same_product"
            verdicts.append(llm.CandidateVerdict(index=i, verdict=verdict, confidence=0.8,
                                                 reason=f"judged {verdict}"))
        return verdicts

    async def fake_compare(ours, theirs, *, usage):
        return llm.ProductMatch(same_product=True, confidence=0.85, reason="Same model name.")

    monkeypatch.setattr(discovery, "fetch_page", fake_fetch)
    monkeypatch.setattr(discovery, "read_product_data", fake_read_product_data)
    monkeypatch.setattr(discovery, "read_price", fake_read_price)
    monkeypatch.setattr(llm, "plan_search", fake_plan)
    monkeypatch.setattr(llm, "judge_candidates", fake_judge)
    monkeypatch.setattr(llm, "compare_products", fake_compare)
    monkeypatch.setattr(search, "search_web", fake_search)
    return calls


@pytest.mark.anyio
async def test_discovery_retries_and_proposes_verified_offers(fake_world):
    user = make_user()
    run = RunLogger.start(user_id=user.id, kind="discovery", title="test")
    await discovery.run_discovery(run, url="https://my-shop.de/sony-xm6")

    with session_scope() as session:
        run_row = session.get(Run, run.run_id)
        product = session.exec(select(Product).where(Product.user_id == user.id)).one()
        offers = session.exec(select(Offer).where(Offer.product_id == product.id)).all()
        events = session.exec(select(RunEvent).where(RunEvent.run_id == run.run_id)
                              .order_by(col(RunEvent.seq))).all()

    assert run_row.status == "completed", run_row.error
    assert run_row.product_id == product.id
    # attempt 1 finds only good-one.de (XM5 has a different EAN, blocked.de fails) → retry
    assert fake_world["plan"] == 2
    by_domain = {o.domain: o for o in offers}
    assert set(by_domain) == {"my-shop.de", "good-one.de", "good-two.de"}
    assert by_domain["my-shop.de"].is_own and by_domain["my-shop.de"].status == "tracking"
    assert by_domain["good-one.de"].status == "proposed"
    assert by_domain["good-one.de"].match_confidence == 0.99  # EAN match beats the LLM
    assert by_domain["good-two.de"].match_reason == "Same model name."

    messages = [e.message for e in events]
    assert any("Different EAN/GTIN" in m for m in messages)
    assert any("blocked.de: rejected" in m for m in messages)
    assert any("attempt 2/2" in m for m in messages)
    assert events[-1].step == "propose"


@pytest.mark.anyio
async def test_discovery_fails_clearly_on_a_non_product_page(fake_world, monkeypatch):
    async def no_product(page, usage=None):
        return ProductData()

    monkeypatch.setattr(discovery, "read_product_data", no_product)
    user = make_user()
    run = RunLogger.start(user_id=user.id, kind="discovery", title="test")
    await discovery.run_discovery(run, url="https://my-shop.de/")
    with session_scope() as session:
        run_row = session.get(Run, run.run_id)
    assert run_row.status == "failed"
    assert "single product page" in run_row.error
