"""Run journal: every agent or scheduler action is a Run with ordered events.

The UI polls `/api/runs/{id}/events?after=<seq>` and renders this journal live — this is
the "transparent agent" part. Events are written immediately, so nothing is lost if the
browser disconnects or the server restarts mid-run.
"""

import asyncio
import logging
from typing import Any

from sqlmodel import select

from backend.config import get_settings
from backend.database import session_scope
from backend.models import Run, RunEvent, utcnow

log = logging.getLogger("rivalscope.runs")
_LEVELS = {
    "info": logging.INFO,
    "success": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}
_background: set[asyncio.Task] = set()


class RunLogger:
    def __init__(self, run_id: int, user_id: int):
        self.run_id = run_id
        self.user_id = user_id
        self._seq = 0

    @classmethod
    def start(
        cls, *, user_id: int, kind: str, title: str, product_id: int | None = None
    ) -> RunLogger:
        with session_scope() as session:
            run = Run(user_id=user_id, kind=kind, title=title, product_id=product_id)
            session.add(run)
            session.commit()
            return cls(run.id, user_id)

    def log(self, step: str, message: str, level: str = "info", **data: Any) -> None:
        self._seq += 1
        with session_scope() as session:
            session.add(
                RunEvent(
                    run_id=self.run_id,
                    seq=self._seq,
                    step=step,
                    level=level,
                    message=message,
                    data=data or None,
                )
            )
            session.commit()
        log.log(_LEVELS.get(level, logging.INFO), "[run %s] %s: %s", self.run_id, step, message)

    def add_usage(self, model: str, tokens_in: int, tokens_out: int) -> None:
        price_in, price_out = get_settings().model_prices.get(model, (0.0, 0.0))
        with session_scope() as session:
            run = session.get(Run, self.run_id)
            run.tokens_in += tokens_in
            run.tokens_out += tokens_out
            run.cost_usd += (tokens_in * price_in + tokens_out * price_out) / 1_000_000
            session.commit()

    def set_product(self, product_id: int) -> None:
        with session_scope() as session:
            run = session.get(Run, self.run_id)
            run.product_id = product_id
            session.commit()

    def finish(
        self, status: str = "completed", *, summary: str | None = None, error: str | None = None
    ) -> None:
        with session_scope() as session:
            run = session.get(Run, self.run_id)
            run.status = status
            run.summary = summary
            run.error = error
            run.finished_at = utcnow()
            session.commit()


def mark_interrupted_runs() -> int:
    """Runs left 'running' by a previous process can't continue — say so honestly."""
    with session_scope() as session:
        runs = session.exec(select(Run).where(Run.status == "running")).all()
        for run in runs:
            run.status = "interrupted"
            run.error = "The server restarted while this run was in progress."
            run.finished_at = utcnow()
        session.commit()
        return len(runs)


def spawn(coro, *, name: str) -> asyncio.Task:
    """Starts a background coroutine, keeps a reference and logs crashes."""
    task = asyncio.create_task(coro, name=name)
    _background.add(task)

    def _done(t: asyncio.Task) -> None:
        _background.discard(t)
        if not t.cancelled() and t.exception():
            log.error("Background task %s crashed", name, exc_info=t.exception())

    task.add_done_callback(_done)
    return task


async def cancel_background() -> None:
    for task in list(_background):
        task.cancel()
    await asyncio.gather(*_background, return_exceptions=True)
