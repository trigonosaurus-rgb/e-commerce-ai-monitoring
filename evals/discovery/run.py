"""Generalization eval of the discovery agent across markets and niches.

    uv run python -m evals.discovery.run                    # all cases
    uv run python -m evals.discovery.run us-hoka-clifton    # selected cases
    uv run python -m evals.discovery.run --fresh            # ignore the search cache

Each case runs the real agent (real OpenAI calls, real page downloads) in a throw-away
database. Tavily answers are cached on disk (`evals/.cache/`), so re-running after a
prompt or code change costs almost no search credits. Proposed matches are scored by
GTIN when both pages have one, otherwise by the hand labels in `labels.json`.
Writes `results/latest.json` and `results/latest.md`.
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
CACHE = HERE.parent / ".cache"
CACHE.mkdir(exist_ok=True)
DB = CACHE / "eval.db"
DB.unlink(missing_ok=True)
os.environ.update(
    {
        "DATABASE_URL": f"sqlite:///{DB.as_posix()}",
        "SCHEDULER_ENABLED": "false",
        "TELEGRAM_BOT_TOKEN": "",
        "SMTP_HOST": "",
    }
)

import httpx  # noqa: E402
from sqlmodel import col, select  # noqa: E402

from backend import search  # noqa: E402
from backend.agent.discovery import run_discovery  # noqa: E402
from backend.config import get_settings  # noqa: E402
from backend.database import init_db, session_scope  # noqa: E402
from backend.events import RunLogger  # noqa: E402
from backend.models import Offer, Product, Run, RunEvent, User  # noqa: E402

SEARCH_CREDITS, EXTRACT_CREDITS = 1, 2  # basic search; advanced extract of one URL


class TavilyMeter:
    """Wraps the Tavily helpers with a disk cache and counts the credits really spent."""

    def __init__(self, fresh: bool):
        self.fresh = fresh
        self.credits = 0
        self.cached_calls = 0
        self._search, self._extract = search.search_web, search.extract_page
        search.search_web, search.extract_page = self.search_web, self.extract_page

    def _path(self, kind: str, key: dict) -> Path:
        digest = hashlib.sha1(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16]
        return CACHE / f"{kind}-{digest}.json"

    async def search_web(self, query: str, **options) -> list[search.SearchResult]:
        path = self._path("search", {"q": query} | options)
        if path.exists() and not self.fresh:
            self.cached_calls += 1
            return [search.SearchResult(**r) for r in json.loads(path.read_text("utf-8"))]
        results = await self._search(query, **options)
        self.credits += SEARCH_CREDITS
        path.write_text(json.dumps([r.__dict__ for r in results], ensure_ascii=False), "utf-8")
        return results

    async def extract_page(self, url: str) -> str | None:
        path = self._path("extract", {"url": url})
        if path.exists() and not self.fresh:
            self.cached_calls += 1
            return json.loads(path.read_text("utf-8"))
        text = await self._extract(url)
        self.credits += EXTRACT_CREDITS if text else 0
        path.write_text(json.dumps(text, ensure_ascii=False), "utf-8")
        return text


def tavily_account_usage() -> int | None:
    key = get_settings().tavily_api_key
    try:
        response = httpx.get(
            "https://api.tavily.com/usage",
            headers={"Authorization": f"Bearer {key.get_secret_value()}"},
            timeout=20,
        )
        return response.json()["account"]["plan_usage"]
    except Exception:
        return None


def score(offer: Offer, labels: dict) -> str:
    """correct | wrong | unlabeled"""
    if (offer.match_reason or "").startswith("Same EAN/GTIN"):
        return "correct"
    label = labels.get(offer.url)
    if label is None:
        return "unlabeled"
    return "correct" if label["correct"] else "wrong"


async def run_case(case: dict, user_id: int, meter: TavilyMeter, labels: dict) -> dict:
    credits_before, cached_before = meter.credits, meter.cached_calls
    run = RunLogger.start(user_id=user_id, kind="discovery", title=f"Eval · {case['id']}")
    started = time.monotonic()
    await run_discovery(run, url=case["url"])
    seconds = round(time.monotonic() - started)

    with session_scope() as session:
        row = session.get(Run, run.run_id)
        product = session.get(Product, row.product_id) if row.product_id else None
        offers = (
            session.exec(
                select(Offer).where(Offer.product_id == product.id, col(Offer.is_own).is_(False))
            ).all()
            if product
            else []
        )
        own = (
            session.exec(
                select(Offer).where(Offer.product_id == product.id, col(Offer.is_own).is_(True))
            ).first()
            if product
            else None
        )
        events = session.exec(
            select(RunEvent).where(RunEvent.run_id == run.run_id).order_by(RunEvent.seq)
        ).all()

    screened = [
        d for e in events if e.step == "screen" for d in (e.data or {}).get("decisions", [])
    ]
    rejected = [
        {"store": e.data.get("store"), "url": e.data.get("url"), "reason": e.data.get("reason")}
        for e in events
        if e.step == "verify" and e.level == "warning" and e.data
    ]
    plans = [e.data for e in events if e.step == "plan_queries" and e.data]
    proposals = [
        {
            "store": o.domain,
            "url": o.url,
            "title": o.title,
            "price": o.last_price,
            "currency": o.currency,
            "confidence": o.match_confidence,
            "reason": o.match_reason,
            "score": score(o, labels),
        }
        for o in offers
    ]
    return {
        "id": case["id"],
        "market": case["market"],
        "niche": case["niche"],
        "url": case["url"],
        "status": row.status,
        "error": row.error,
        "product": (
            {
                "name": product.name,
                "brand": product.brand,
                "gtin": product.gtin,
                "mpn": product.mpn,
                "market": product.market,
                "price": own.last_price if own else None,
                "currency": product.currency,
            }
            if product
            else None
        ),
        "queries": [q for p in plans for q in p.get("queries", [])],
        "retailers": [r for p in plans for r in p.get("retailers", [])],
        "attempts": len(plans),
        "screened": len(screened),
        "screen_kept": sum(1 for d in screened if d.get("kept")),
        "verify_rejected": rejected,
        "proposals": proposals,
        "correct": sum(1 for p in proposals if p["score"] == "correct"),
        "wrong": sum(1 for p in proposals if p["score"] == "wrong"),
        "unlabeled": sum(1 for p in proposals if p["score"] == "unlabeled"),
        "tavily_credits": meter.credits - credits_before,
        "tavily_cached_calls": meter.cached_calls - cached_before,
        "llm_cost_usd": round(row.cost_usd, 4),
        "seconds": seconds,
    }


def money(value, currency) -> str:
    return "—" if value is None else f"{value:,.2f} {currency or ''}".strip()


def markdown(results: list[dict], account_delta: int | None) -> str:
    total = {
        k: sum(r[k] for r in results)
        for k in ("correct", "wrong", "unlabeled", "tavily_credits", "seconds")
    }
    cost = sum(r["llm_cost_usd"] for r in results)
    scored = total["correct"] + total["wrong"]
    precision = f"{total['correct'] / scored:.0%}" if scored else "—"
    found = sum(1 for r in results if r["correct"])
    lines = [
        "# Discovery agent — cross-market eval",
        "",
        f"{len(results)} cases · cases with ≥1 correct match: {found}/{len(results)} · "
        f"proposals: {total['correct']} correct, {total['wrong']} wrong, "
        f"{total['unlabeled']} unlabeled · precision {precision}",
        f"Tavily credits spent this run: {total['tavily_credits']}"
        + (f" (account counter: +{account_delta})" if account_delta is not None else "")
        + f" · LLM ${cost:.3f} · {total['seconds'] // 60} min",
        "",
        "| Case | Market | Read as | Proposed | ✓ | ✗ | ? | Credits | LLM $ |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        p = r["product"] or {}
        read = (
            f"{p.get('name') or '—'} · {money(p.get('price'), p.get('currency'))}"
            if p
            else f"failed: {r['error']}"
        )
        lines.append(
            f"| {r['id']} | {r['market']} | {read[:70]} | {len(r['proposals'])} | "
            f"{r['correct']} | {r['wrong']} | {r['unlabeled']} | {r['tavily_credits']} | "
            f"{r['llm_cost_usd']:.3f} |"
        )
    for r in results:
        p = r["product"] or {}
        lines += [
            "",
            f"## {r['id']} — {r['niche']}",
            "",
            f"- Page: {r['url']}",
            f"- Read: {p.get('name')} · brand {p.get('brand')} · GTIN {p.get('gtin')} · "
            f"MPN {p.get('mpn')} · {money(p.get('price'), p.get('currency'))} · "
            f"market {p.get('market')}",
            f"- Status: {r['status']}" + (f" ({r['error']})" if r["error"] else ""),
            f"- Attempts: {r['attempts']} · queries: {'; '.join(r['queries'])}",
            f"- Retailers guessed: {', '.join(r['retailers']) or '—'}",
            f"- Screened {r['screened']} pages, kept {r['screen_kept']}",
        ]
        for o in r["proposals"]:
            mark = {"correct": "✓", "wrong": "✗", "unlabeled": "?"}[o["score"]]
            lines.append(
                f"- {mark} **{o['store']}** {money(o['price'], o['currency'])} "
                f"(conf. {o['confidence']}) — {o['reason']} <{o['url']}>"
            )
        for x in r["verify_rejected"]:
            lines.append(f"- rejected at verify: {x['store']} — {x['reason']}")
    return "\n".join(lines) + "\n"


async def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("only", nargs="*", help="case ids to run (default: all)")
    parser.add_argument("--fresh", action="store_true", help="don't use cached Tavily answers")
    args = parser.parse_args()

    cases = json.loads((HERE / "cases.json").read_text("utf-8"))
    if args.only:
        cases = [c for c in cases if c["id"] in args.only]
    labels_path = HERE / "labels.json"
    labels = json.loads(labels_path.read_text("utf-8")) if labels_path.exists() else {}

    init_db()
    with session_scope() as session:
        user = User(email="eval@localhost")
        session.add(user)
        session.commit()
        user_id = user.id
    meter = TavilyMeter(fresh=args.fresh)
    usage_before = tavily_account_usage()
    results = []
    for case in cases:
        print(f"→ {case['id']} ({case['market']})", flush=True)
        result = await run_case(case, user_id, meter, labels)
        print(
            f"  {result['status']}: {len(result['proposals'])} proposed, "
            f"{result['correct']} correct, {result['wrong']} wrong, "
            f"{result['tavily_credits']} credits, {result['seconds']} s",
            flush=True,
        )
        results.append(result)
    usage_after = tavily_account_usage()
    delta = usage_after - usage_before if None not in (usage_before, usage_after) else None

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    if args.only and (out / "latest.json").exists():  # keep the other cases' last results
        fresh = {r["id"]: r for r in results}
        old = {r["id"]: r for r in json.loads((out / "latest.json").read_text("utf-8"))}
        order = [c["id"] for c in json.loads((HERE / "cases.json").read_text("utf-8"))]
        results = [fresh.get(i) or old[i] for i in order if i in fresh or i in old]
    (out / "latest.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (out / "latest.md").write_text(markdown(results, delta), encoding="utf-8")
    print(f"Report: {out / 'latest.md'}")


if __name__ == "__main__":
    asyncio.run(main())
