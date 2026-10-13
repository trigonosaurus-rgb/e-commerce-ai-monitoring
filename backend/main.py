"""Application entry point: `uv run uvicorn backend.main:app --reload`.

Startup: create tables → make sure the demo workspace exists → mark runs that were cut
off by a restart as interrupted → start the price-check scheduler and the Telegram bot.
The built frontend (frontend/out) is served from the same process, so in production the
whole product is one service on one port.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import account, products, runs
from backend.auth import ensure_demo_user
from backend.config import ROOT_DIR, get_settings
from backend.database import init_db, session_scope
from backend.events import cancel_background, mark_interrupted_runs, spawn
from backend.notify.telegram import poller
from backend.scheduler import scheduler

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1251/cp437
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("rivalscope")

FRONTEND_DIR = ROOT_DIR / "frontend" / "out"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    init_db()
    with session_scope() as session:
        ensure_demo_user(session)
    if interrupted := mark_interrupted_runs():
        log.warning("Marked %s run(s) as interrupted by the previous shutdown", interrupted)
    tasks = []
    if settings.scheduler_enabled:
        tasks.append(spawn(scheduler.run_forever(), name="scheduler"))
    if settings.telegram_configured:
        tasks.append(spawn(poller.run_forever(), name="telegram-poller"))
    log.info(
        "%s started · AI=%s search=%s telegram=%s email=%s",
        settings.app_name,
        settings.llm_configured,
        settings.search_configured,
        settings.telegram_configured,
        settings.email_configured,
    )
    yield
    await cancel_background()
    await asyncio.sleep(0)


app = FastAPI(title="Rivalscope API", version="0.2.0", lifespan=lifespan)
for module in (products, runs, account):
    app.include_router(module.router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", [])[1:]) or "request"
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "invalid_input",
                "message": f"{field}: {first.get('msg', 'invalid value')}",
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error(_request: Request, exc: Exception):
    log.exception("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "internal_error",
                "message": "Something went wrong on our side. It has been logged.",
            }
        },
    )


if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
