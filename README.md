# Rivalscope — competitor price monitoring with an AI agent you can audit

[![CI](https://github.com/trigonosaurus-rgb/e-commerce-ai-monitoring/actions/workflows/ci.yml/badge.svg)](https://github.com/trigonosaurus-rgb/e-commerce-ai-monitoring/actions/workflows/ci.yml)
![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-009688)
![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C)
![Next.js 16](https://img.shields.io/badge/Next.js-16-black)

Paste a product page from your store. An AI agent finds the same product in other online stores,
checks their prices on a schedule and tells you when a competitor undercuts you — and **every number
comes with the page fragment it was read from**, so nothing has to be taken on trust.

![Dashboard](docs/screenshots/dashboard.png)

## What it does

- **Finds your competitors.** A LangGraph agent reads your product (name, brand, EAN, price), plans
  searches for your market, screens the results, opens each candidate store and verifies that it
  sells the *same* product. Matches are proposed — you approve what gets tracked.
- **Monitors prices.** Approved pages are re-checked every few hours. Prices come from the
  structured data stores publish for Google Shopping; the LLM is only a fallback.
- **Shows its work.** Every agent run is a journal: what it searched, which results it kept or
  rejected and why, what each step cost. Every price links to its evidence.
- **Alerts you** in the app, on Telegram or by email when a competitor drops below you, changes
  price or goes out of stock — with a short AI summary built only from numbers computed in code.

| The agent at work | Evidence behind a price |
|---|---|
| ![Agent journal](docs/screenshots/agent-journal.png) | ![Evidence](docs/screenshots/evidence.png) |

## How it works

```mermaid
flowchart LR
    subgraph Discovery agent · once per product
        A[Read your page] --> B[Plan searches]
        B --> R[Research the market<br/>who sells this kind of product]
        R --> C[Web search<br/>Tavily]
        C --> D[Screen results<br/>LLM]
        D --> E[Verify each store<br/>price + same product]
        E -- fewer than 2 matches --> B
        E --> F[Propose matches]
    end
    F --> H{You approve}
    subgraph Monitoring · every 12 h
        G[Fetch page] --> I[Read price<br/>JSON-LD → LLM fallback]
        I --> J[Sanity checks]
        J --> K[Snapshot + evidence]
        K --> L[Compare & alert]
    end
    H --> G
```

**Researching the market.** Before looking for the product itself, the agent searches for
this *kind* of product in the market ("gooseneck electric kettle shop", "autocuiseur 7,5 L
acheter") to see which stores sell it right now. Retailers the model knows from training are
added only if their domain exists, shops on another country's domain are dropped, and the model
sorts the rest into online shops, brand shops, marketplaces, comparison sites and magazines —
every decision with a reason in the run timeline. The product is then searched on the shops
that are left.

**Matching the same product.** EAN/GTIN codes decide when both pages have them (they usually do);
otherwise the manufacturer part number; only then the LLM compares the two listings. Used,
refurbished and other-market offers (other country or currency) are rejected with a reason.

**Reading a price.** Most shops (Shopify, WooCommerce, Shopware, Magento, big retailers) publish
schema.org `Product`/`Offer` JSON-LD — exact and free. Pages without it go to the LLM, which must
quote the page text it read the price from; the quote is checked against the page. Pages are
requested the way a local customer sees them: multi-country shops (Shopify "markets") get a
country hint, otherwise a UK shop shows a visitor from Germany its price without VAT. If a store
refuses the request, Rivalscope asks once more as an openly named crawler (`RivalscopeBot`) —
many Shopify stores welcome that — and only then pays for Tavily Extract. It never disguises
itself or bypasses bot protection: a blocked page is shown as blocked.

**Not trusting a single reading.** A price that moves more than 60% in one check, or changes
currency, is stored as evidence but flagged for review instead of triggering an alert.

## Design decisions

| Decision | Why |
|---|---|
| Structured data first, LLM second | Deterministic, free and exact for most stores; the LLM handles the rest and is verified. |
| Human approval of matches | LLM product matching is good, not perfect. One click keeps wrong data out of the history. |
| Numbers in Python, words from the LLM | Alerts never contain invented numbers — the model only explains figures it is given. |
| LangGraph only for discovery | That flow has a real loop (retry with different searches). Scheduled checks are plain code. |
| State in the database, not in memory | Restarts lose nothing: overdue checks run on the next tick, cut-off runs are marked *interrupted*. |
| Polling instead of SSE | Works through any proxy, needs no reconnection logic; the UI feels just as live at 1.5 s. |
| One service | The Next.js app is exported to static files and served by FastAPI: one image, one port, same-origin cookies. |
| SSRF guard on every redirect hop | Users submit URLs the server fetches; private, loopback and metadata addresses are refused. |

## Evaluation

The discovery agent was first tuned on German stores, so it was tested on 10 products from
other markets and niches ([cases](evals/discovery/cases.json),
[full report](evals/discovery/results/latest.md)): branded goods with and without barcodes,
running shoes in one colourway, a specialty-coffee kettle, a small designer's tea towel, and a
shop's own-brand tin as a negative control.

| Market | Cases | Correct matches proposed | Wrong |
|---|---|---|---|
| United States | 3 | 12 | 0 |
| United Kingdom | 3 | 5 (none expected for the own-brand tin) | 0 |
| France | 2 | 7 | 0 |
| Netherlands | 1 | 0 (product discontinued, no store found) | 0 |
| Poland (PLN) | 1 | 2 | 0 |

What the first run found and what changed:
[baseline](evals/discovery/results/baseline.md) — 17 correct, 2 wrong.

- Retailers came from the model's memory, written as free text: "sur la table.com" made the
  search API reject the whole retailer search in 5 of 10 runs. Domains are now constrained by
  a pattern in the structured-output schema, and the retailer list comes from the market
  research step above instead of memory alone.
- The research step first kept other brands' own shops (Smithey for a Lodge skillet, Nike for
  HOKA shoes) and shops of neighbouring countries (Belgian stores for the Dutch market); both
  are filtered now.
- A name-only match at about twice our price was a 60 ml bottle instead of 30 ml; without a
  shared barcode or part number such a gap now rejects the match.
- Structured data often drops the variant: a shoe page says "HOKA Clifton 10" while its title
  says "Men's … Raw Linen/Stone". The page title is now part of the product identity, and
  editions (Pro, Studio, SE, bundles) and other-country shops in the same currency are rejected.
- Shopify stores answered a browser-like client with HTTP 429, a UK store showed a price without
  VAT to a visitor abroad, and a deleted product redirected to the home page, whose featured
  product would have been read instead (see "Reading a price").

Honest caveats: matches are labelled by hand (a shared barcode counts automatically), the rules
were adjusted after the baseline on the same 10 cases, and results vary between runs — the same
case found 0 matches in one run and 3 in the next, because search results and the screening
model's choices differ. An outlet for customer returns once passed as new (it didn't say so in
its product data); approval by a person remains the last check. Recall is not measured — big chains
(John Lewis, Currys, Amazon, Sephora, REI) often render prices with JavaScript or block both
direct requests and the backup reader, so they rarely appear among the matches. Re-run with
`uv run python -m evals.discovery.run`; search answers are cached, but the model plans slightly
different queries each time, so a full run costs about 60 Tavily credits and $0.04 in AI.

## Cost

Measured on real runs (OpenAI `gpt-6-luna` for extraction/screening, `gpt-6.1-sol` for alert text):

| What | Typical cost |
|---|---|
| Discovery run (find competitors for one product) | $0.002–0.005 + 5–10 Tavily credits |
| Scheduled check of a product with 4–7 pages | $0 when stores publish structured data, ~$0.0005 otherwise |
| 20 products × 4 competitors, checked twice a day | ≈ $2–4 / month in AI + Tavily free tier |

Each run's tokens and cost are shown in the UI.

## Run it locally

Requirements: [uv](https://docs.astral.sh/uv/), Node.js 24, an OpenAI key and a Tavily key.

```bash
git clone https://github.com/trigonosaurus-rgb/e-commerce-ai-monitoring.git
cd e-commerce-ai-monitoring
cp .env.example .env            # add OPENAI_API_KEY and TAVILY_API_KEY

uv sync                         # backend dependencies
uv run python -m backend.cli create-user you@example.com   # prints a password
uv run uvicorn backend.main:app --reload --port 8000

cd frontend && npm ci && npm run dev    # http://localhost:3000
```

Anonymous visitors see the read-only demo workspace; sign in to use your own. Access is
invite-only: accounts are created with the CLI, and the "Request access" form forwards requests
to the owner's Telegram.

```bash
uv run python -m backend.cli access-requests        # list requests
uv run python -m backend.cli export-demo you@example.com demo.json
uv run python -m backend.cli seed-demo demo.json    # load a workspace into the public demo
```

Price checks run inside the server. To collect history without keeping it running, schedule
`uv run python -m backend.cli check-due` (cron, or `scripts/schedule-checks.ps1` on Windows):
it runs the checks that are due and exits.

### Docker

```bash
docker build -t rivalscope .
docker run -p 8000:8000 --env-file .env -v rivalscope-data:/app/data rivalscope
```

The image contains the API, the scheduler, the Telegram bot and the built web app. Run a single
container per database: the scheduler lives inside the process.

### Notifications

- **Telegram:** create a bot with [@BotFather](https://t.me/BotFather) and set
  `TELEGRAM_BOT_TOKEN` (the bot's name is read from Telegram). Users connect their chat in
  Settings (no webhook needed).
- **Email:** any SMTP server (`SMTP_*` variables). Use a sending service such as
  [Resend](https://resend.com/docs/send-with-smtp) rather than a personal mailbox: its key can
  only send mail. Until your domain is verified there, it delivers only to your own address.

## Quality

- 66 tests run offline (`uv run pytest`): price extraction on real-world page shapes, SSRF
  protection, monitoring rules, the agent graph with a fake web/LLM, the API, demo read-only mode.
- `ruff` for the backend, ESLint + TypeScript for the frontend, migrations checked against the
  models, Docker build — all in [CI](.github/workflows/ci.yml).
- `/api/health` and the Settings page show the database, scheduler, AI, search, Telegram and
  email status at a glance.

## Project structure

```
backend/
  agent/discovery.py   LangGraph agent that finds competitors
  monitor.py           price checks, sanity rules, alerts
  scheduler.py         background loop driven by Offer.next_check_at
  extraction.py        JSON-LD / microdata / meta parsing + verified LLM fallback
  fetching.py          safe page fetching (SSRF guard, Tavily fallback)
  llm.py               every OpenAI call, as typed Pydantic outputs
  events.py            the run journal shown in the UI
  notify/              Telegram and email delivery
  api/                 FastAPI routers;  auth.py: sessions, demo workspace
  migrations/          Alembic migrations, applied on startup
evals/discovery/       cross-market eval of the agent: cases, labels, reports
frontend/src/
  app/                 dashboard, product, agent run, activity, alerts, settings, login
  lib/                 typed API client, data hooks, formatting
```

## Limitations

- Sites with aggressive bot protection or JavaScript-only prices (e.g. Amazon, John Lewis,
  Currys, Sephora) are often unreadable and shown as blocked or "no price found".
- Product variants (size, color) are matched carefully, but the final word is the user's approval.
- Prices are compared only within one currency; other markets are out of scope by design.
- Price history in the demo is real and grows with time — it started in October 2026.

## License

MIT
