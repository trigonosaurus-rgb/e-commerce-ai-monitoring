"""Discovery agent: finds the same product in other online stores.

    read_product → plan_queries → search → screen → verify ─┬─> propose
                        ^                                   │
                        └──── fewer than 2 matches (max 2 attempts)

* read_product  — reads your page: name, brand, model, EAN and your price.
* plan_queries  — LLM writes search queries (with feedback on a retry).
* search        — Tavily web search in the product's market, one result per store.
* screen        — LLM sorts results: same product / other model / marketplace / article.
* verify        — opens each shortlisted page, reads its price and confirms it is the same
                  product (EAN match first, LLM comparison only when there is no EAN).
* propose       — saves matches as "proposed": a human approves them before tracking.

Every step writes to the run journal, so the UI shows what was found, kept and rejected.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from sqlmodel import col, select

from backend import llm, search
from backend.config import get_settings
from backend.database import session_scope
from backend.events import RunLogger
from backend.extraction import normalize_code, normalize_gtin, read_product_data
from backend.fetching import FetchError, fetch_page
from backend.models import Offer, PriceSnapshot, Product, utcnow
from backend.monitor import fmt_money, read_price

log = logging.getLogger(__name__)
MAX_ATTEMPTS = 2
ENOUGH_OFFERS = 2
MIN_SCREEN_CONFIDENCE = 0.5


class DiscoveryError(RuntimeError):
    pass


@dataclass
class DiscoveryContext:
    run: RunLogger
    user_id: int


class DiscoveryState(TypedDict, total=False):
    url: str | None
    product_id: int | None
    product: dict  # name, brand, mpn, gtin
    currency: str | None
    market: str | None
    excluded_domains: list[str]
    tried_queries: list[str]
    queries: list[str]
    retailers: list[str]  # stores the LLM expects to carry the product
    retailer_query: str | None
    tried_retailers: list[str]
    seen_urls: list[str]
    candidates: list[dict]
    shortlist: list[dict]
    verified: list[dict]
    rejections: list[str]
    attempt: int


def _room_left(product_id: int) -> int:
    with session_scope() as session:
        taken = session.exec(
            select(Offer).where(
                Offer.product_id == product_id,
                col(Offer.is_own).is_(False),
                Offer.status != "rejected",
            )
        ).all()
    return max(get_settings().max_offers_per_product - len(taken), 0)


def clean_domain(raw: str) -> str | None:
    """The model sometimes writes "sur la table.com"; one bad domain makes the whole
    retailer search fail, so spaces are dropped and anything still invalid is skipped."""
    text = re.sub(r"\s+", "", raw.lower()).removeprefix("https://").removeprefix("http://")
    domain = search.domain_of("https://" + text)
    return domain if re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", domain) else None


# ------------------------------------------------------------------------------ nodes


async def read_product(state: DiscoveryState, runtime: Runtime[DiscoveryContext]) -> dict:
    run, settings = runtime.context.run, get_settings()
    if state.get("product_id"):  # "find more competitors" for an existing product
        with session_scope() as session:
            product = session.get(Product, state["product_id"])
            offers = session.exec(select(Offer).where(Offer.product_id == product.id)).all()
        run.log(
            "read_product",
            f"Looking for more stores selling {product.name}",
            product={"name": product.name, "brand": product.brand, "gtin": product.gtin},
        )
        own = next((o for o in offers if o.is_own), None)
        return {
            "product": {
                "name": product.name,
                "brand": product.brand,
                "mpn": product.mpn,
                "gtin": product.gtin,
            },
            "url": own.url if own else None,
            "currency": product.currency,
            "market": product.market,
            "excluded_domains": sorted({o.domain for o in offers}),
            "seen_urls": [o.url for o in offers],
            "tried_queries": [],
            "verified": [],
            "rejections": [],
            "attempt": 0,
        }

    url = state["url"]
    run.log("read_product", "Reading your product page", url=url)
    page = await fetch_page(url)
    data = await read_product_data(page, usage=run)
    if not data.name:
        raise DiscoveryError(
            "Couldn't find a product on this page. Use the link of a single "
            "product page, not a category or home page."
        )
    domain = search.domain_of(page.url)
    with session_scope() as session:
        product = Product(
            user_id=runtime.context.user_id,
            name=data.name,
            brand=data.brand,
            mpn=data.mpn,
            gtin=data.gtin,
            image_url=data.image,
            currency=data.currency,
        )
        session.add(product)
        session.flush()
        own = Offer(
            product_id=product.id,
            is_own=True,
            store=domain,
            domain=domain,
            url=page.url,
            status="tracking",
            source="manual",
            title=data.name,
            last_price=data.price if data.has_price else None,
            currency=data.currency,
            in_stock=data.in_stock,
            last_checked_at=utcnow(),
            next_check_at=utcnow() + timedelta(hours=settings.check_interval_hours),
        )
        session.add(own)
        session.flush()
        if data.has_price:
            session.add(
                PriceSnapshot(
                    offer_id=own.id,
                    run_id=run.run_id,
                    price=data.price,
                    currency=data.currency,
                    in_stock=data.in_stock,
                    method=data.method,
                    fetched_via=page.via,
                    evidence=data.evidence,
                )
            )
        session.commit()
        product_id = product.id
    run.set_product(product_id)

    identity = data.identity()
    if data.has_price:
        run.log(
            "read_product",
            f"Found “{data.name}” at {fmt_money(data.price, data.currency)}",
            level="success",
            product=identity,
            price=data.price,
            currency=data.currency,
            method=data.method,
            evidence=data.evidence[:300],
            url=page.url,
        )
    else:
        run.log(
            "read_product",
            f"Found “{data.name}”, but not your price ({data.note}). "
            "Competitors will still be searched.",
            level="warning",
            product=identity,
        )
    return {
        "product_id": product_id,
        "product": identity,
        "currency": data.currency,
        "market": None,
        "excluded_domains": [domain],
        "seen_urls": [url, page.url],
        "tried_queries": [],
        "verified": [],
        "rejections": [],
        "attempt": 0,
    }


async def plan_queries(state: DiscoveryState, runtime: Runtime[DiscoveryContext]) -> dict:
    run = runtime.context.run
    attempt = state["attempt"] + 1
    if attempt > 1:
        run.log(
            "plan_queries",
            f"Only {len(state['verified'])} match(es) so far — trying "
            f"different searches (attempt {attempt}/{MAX_ATTEMPTS})",
            level="warning",
        )
    tried_retailers = state.get("tried_retailers", [])
    plan = await llm.plan_search(
        state["product"],
        store_url=state.get("url") or "",
        previous=state["tried_queries"],
        previous_retailers=tried_retailers,
        feedback=state["rejections"],
        usage=run,
    )
    queries = [q.strip() for q in plan.queries if q.strip()]
    gtin = state["product"].get("gtin")
    if gtin and gtin not in state["tried_queries"]:
        queries.append(gtin)
    queries = [q for q in dict.fromkeys(queries) if q not in state["tried_queries"]][:4]
    retailers = [clean_domain(d) for d in plan.retailer_domains]
    skip = set(tried_retailers) | set(state["excluded_domains"])
    retailers = [d for d in dict.fromkeys(retailers) if d and d not in skip][:10]
    market = state.get("market") or plan.market_country
    with session_scope() as session:
        product = session.get(Product, state["product_id"])
        if market and not product.market:
            product.market = market
            session.commit()
    run.log(
        "plan_queries",
        f"Searching {len(queries)} queries"
        + (f" in the {market.title()} market" if market else "")
        + (f" and {len(retailers)} likely retailers" if retailers else ""),
        queries=queries,
        retailers=retailers,
        market=market,
    )
    return {
        "queries": queries,
        "tried_queries": state["tried_queries"] + queries,
        "retailers": retailers,
        "retailer_query": plan.retailer_query,
        "tried_retailers": tried_retailers + retailers,
        "market": market,
        "attempt": attempt,
    }


async def search_stores(state: DiscoveryState, runtime: Runtime[DiscoveryContext]) -> dict:
    run = runtime.context.run
    seen, excluded = set(state["seen_urls"]), set(state["excluded_domains"])
    searches = [(q, {"exclude_domains": sorted(excluded)}) for q in state["queries"]]
    retailers = [d for d in state.get("retailers", []) if d not in excluded]
    if retailers and state.get("retailer_query"):
        # web search restricted to the named stores: finds their product pages directly
        searches.append(
            (state["retailer_query"], {"include_domains": retailers, "max_results": 15})
        )
    results: list[search.SearchResult] = []
    for query, options in searches:
        try:
            results += await search.search_web(query, country=state.get("market"), **options)
        except Exception as exc:
            run.log("search", f"Search for “{query}” failed: {exc}", level="warning")
    candidates, per_domain = [], {}
    for r in results:
        # up to 2 pages per store: the first hit is sometimes a category page
        if r.url in seen or r.domain in excluded or per_domain.get(r.domain, 0) >= 2:
            continue
        seen.add(r.url)
        per_domain[r.domain] = per_domain.get(r.domain, 0) + 1
        candidates.append(
            {
                "url": r.url,
                "title": r.title,
                "snippet": r.snippet,
                "domain": r.domain,
                "favicon": r.favicon,
            }
        )
    run.log(
        "search",
        f"{len(results)} results → {len(candidates)} new page(s) from {len(per_domain)} "
        "store(s) to screen",
        results=[{k: c[k] for k in ("title", "url", "domain", "favicon")} for c in candidates],
    )
    return {
        "candidates": candidates,
        "seen_urls": state["seen_urls"] + [c["url"] for c in candidates],
    }


async def screen(state: DiscoveryState, runtime: Runtime[DiscoveryContext]) -> dict:
    run = runtime.context.run
    candidates = state["candidates"]
    if not candidates:
        return {"shortlist": []}
    judged = await llm.judge_candidates(
        state["product"],
        candidates,
        market=state.get("market"),
        currency=state.get("currency"),
        usage=run,
    )
    verdicts = {v.index: v for v in judged}
    decisions, accepted, notes = [], [], []
    for i, c in enumerate(candidates):
        v = verdicts.get(i)
        keep = bool(v and v.verdict == "same_product" and v.confidence >= MIN_SCREEN_CONFIDENCE)
        reason = v.reason if v else "The model gave no verdict."
        decisions.append(
            {
                "domain": c["domain"],
                "url": c["url"],
                "title": c["title"],
                "favicon": c.get("favicon"),
                "verdict": v.verdict if v else "unknown",
                "confidence": v.confidence if v else 0,
                "reason": reason,
                "kept": keep,
            }
        )
        if keep:
            accepted.append(c | {"confidence": v.confidence, "reason": reason})
        else:
            notes.append(f"{c['domain']}: {reason}")
    room = _room_left(state["product_id"]) - len(state["verified"])
    best_per_store: dict[str, dict] = {}
    for c in sorted(accepted, key=lambda c: -c["confidence"]):
        best_per_store.setdefault(c["domain"], c)
    shortlist = list(best_per_store.values())[: max(room, 0) + 2]
    run.log(
        "screen",
        f"{len(accepted)} of {len(candidates)} look like the same product",
        level="success" if accepted else "warning",
        decisions=decisions,
    )
    return {"shortlist": shortlist, "rejections": state["rejections"] + notes}


async def verify(state: DiscoveryState, runtime: Runtime[DiscoveryContext]) -> dict:
    run = runtime.context.run
    product = state["product"]
    limit = asyncio.Semaphore(4)

    async def check(c: dict) -> tuple[dict, dict | None, str]:
        async with limit:
            try:
                reading, data = await read_price(c["url"], run, state.get("market"))
            except (FetchError, llm.LLMError) as exc:
                return c, None, str(exc)
        currency = state.get("currency")
        if currency and reading.currency != currency:
            return c, None, f"Sells in {reading.currency}, outside your market ({currency})."
        if data.condition in ("used", "refurbished"):
            return c, None, f"Sells it {data.condition}, not new."
        ours, theirs = normalize_gtin(product.get("gtin")), normalize_gtin(data.gtin)
        if ours and theirs:
            if ours != theirs:
                return c, None, f"Different EAN/GTIN ({data.gtin} vs {product['gtin']})."
            confidence, reason = 0.99, "Same EAN/GTIN code on both pages."
        elif normalize_code(product.get("mpn")) and (
            normalize_code(product.get("mpn")) == normalize_code(data.mpn)
        ):
            confidence, reason = 0.9, f"Same manufacturer part number ({data.mpn})."
        else:
            try:
                match = await llm.compare_products(
                    product,
                    {"page_title": c["title"]} | data.identity(),  # their own <title> wins
                    usage=run,
                )
            except llm.LLMError as exc:
                return c, None, str(exc)
            if not match.same_product:
                return c, None, match.reason
            confidence, reason = min(match.confidence, c["confidence"]), match.reason
        offer = {
            "url": reading.page_url,
            "domain": c["domain"],
            "title": data.name or c["title"],
            "price": reading.price,
            "currency": reading.currency,
            "in_stock": reading.in_stock,
            "method": reading.method,
            "via": reading.via,
            "evidence": reading.evidence,
            "confidence": round(confidence, 2),
            "reason": reason,
        }
        return c, offer, reason

    verified, notes = list(state["verified"]), []
    for c, offer, reason in await asyncio.gather(*(check(c) for c in state["shortlist"])):
        if offer:
            verified.append(offer)
            run.log(
                "verify",
                f"{c['domain']}: {fmt_money(offer['price'], offer['currency'])} — {reason}",
                level="success",
                url=offer["url"],
                price=offer["price"],
                currency=offer["currency"],
                evidence=offer["evidence"][:300],
                confidence=offer["confidence"],
                method=offer["method"],
                store=c["domain"],
                reason=reason,
            )
        else:
            notes.append(f"{c['domain']}: {reason}")
            run.log(
                "verify",
                f"{c['domain']}: rejected — {reason}",
                level="warning",
                url=c["url"],
                store=c["domain"],
                reason=reason,
            )
    return {"verified": verified, "rejections": state["rejections"] + notes}


def after_verify(state: DiscoveryState) -> str:
    enough = len(state["verified"]) >= ENOUGH_OFFERS
    return "propose" if enough or state["attempt"] >= MAX_ATTEMPTS else "plan_queries"


async def propose(state: DiscoveryState, runtime: Runtime[DiscoveryContext]) -> dict:
    run = runtime.context.run
    to_save = sorted(state["verified"], key=lambda o: -o["confidence"])
    to_save = to_save[: _room_left(state["product_id"])]
    with session_scope() as session:
        for o in to_save:
            offer = Offer(
                product_id=state["product_id"],
                store=o["domain"],
                domain=o["domain"],
                url=o["url"],
                status="proposed",
                source="agent",
                title=o["title"],
                match_confidence=o["confidence"],
                match_reason=o["reason"],
                last_price=o["price"],
                currency=o["currency"],
                in_stock=o["in_stock"],
                last_checked_at=utcnow(),
            )
            session.add(offer)
            session.flush()
            session.add(
                PriceSnapshot(
                    offer_id=offer.id,
                    run_id=run.run_id,
                    price=o["price"],
                    currency=o["currency"],
                    in_stock=o["in_stock"],
                    method=o["method"],
                    fetched_via=o["via"],
                    evidence=o["evidence"],
                )
            )
        session.commit()
    if to_save:
        run.log(
            "propose",
            f"{len(to_save)} competitor offer(s) are ready for your review",
            level="success",
            offers=[
                {k: o[k] for k in ("domain", "url", "price", "currency", "confidence")}
                for o in to_save
            ],
        )
    else:
        run.log(
            "propose",
            "No matching offers found. You can add competitor links manually.",
            level="warning",
        )
    return {"verified": to_save}


def build_graph():
    graph = StateGraph(DiscoveryState, context_schema=DiscoveryContext)
    graph.add_node("read_product", read_product)
    graph.add_node("plan_queries", plan_queries)
    graph.add_node("search", search_stores)
    graph.add_node("screen", screen)
    graph.add_node("verify", verify)
    graph.add_node("propose", propose)
    graph.add_edge(START, "read_product")
    graph.add_edge("read_product", "plan_queries")
    graph.add_edge("plan_queries", "search")
    graph.add_edge("search", "screen")
    graph.add_edge("screen", "verify")
    graph.add_conditional_edges("verify", after_verify, ["plan_queries", "propose"])
    graph.add_edge("propose", END)
    return graph.compile()


GRAPH = build_graph()


async def run_discovery(
    run: RunLogger, *, url: str | None = None, product_id: int | None = None
) -> None:
    try:
        final = await GRAPH.ainvoke(
            {"url": url, "product_id": product_id},
            context=DiscoveryContext(run=run, user_id=run.user_id),
        )
        found = len(final.get("verified", []))
        run.finish(
            summary=f"{found} competitor offer(s) proposed" if found else "No matching offers found"
        )
    except (DiscoveryError, FetchError, llm.LLMError, search.SearchNotConfigured) as exc:
        run.log("error", str(exc), level="error")
        run.finish("failed", error=str(exc))
    except Exception as exc:
        log.exception("Discovery run %s crashed", run.run_id)
        run.log("error", f"Unexpected error: {exc}", level="error")
        run.finish("failed", error=str(exc))
