"""Background loop that runs price checks when they are due.

All scheduling state lives in the database (`Offer.next_check_at`), so a restart loses
nothing: overdue checks simply run on the next tick.
"""

import asyncio
import logging
from collections import defaultdict

from sqlmodel import select

from backend import monitor
from backend.database import session_scope
from backend.events import RunLogger
from backend.models import Offer, Product, utcnow

log = logging.getLogger(__name__)
TICK_SECONDS = 60
MAX_PRODUCTS_PER_TICK = 20


class CheckAlreadyRunning(RuntimeError):
    pass


class Scheduler:
    def __init__(self) -> None:
        self.status = "stopped"
        self.last_tick = None
        self.active: set[int] = set()  # product ids being checked right now

    async def run_forever(self) -> None:
        self.status = "running"
        while True:
            try:
                await self.tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Scheduler tick failed")
            await asyncio.sleep(TICK_SECONDS)

    async def tick(self) -> int:
        """Checks every product with due pages; returns how many products were checked."""
        self.last_tick = utcnow()
        with session_scope() as session:
            due = session.exec(
                select(Offer.id, Offer.product_id).where(
                    Offer.status == "tracking", Offer.next_check_at <= utcnow()
                )
            ).all()
        by_product: dict[int, list[int]] = defaultdict(list)
        for offer_id, product_id in due:
            by_product[product_id].append(offer_id)
        checked = 0
        for product_id in list(by_product)[:MAX_PRODUCTS_PER_TICK]:
            try:
                run = self.begin(product_id, "Scheduled check")
            except CheckAlreadyRunning:
                continue
            await self.execute(run, product_id, by_product[product_id])
            checked += 1
        return checked

    def begin(self, product_id: int, label: str) -> RunLogger:
        """Reserves the product and opens a Run (fast, so the API can return its id)."""
        if product_id in self.active:
            raise CheckAlreadyRunning("A check for this product is already running.")
        with session_scope() as session:
            product = session.get(Product, product_id)
        run = RunLogger.start(
            user_id=product.user_id,
            kind="check",
            title=f"{label} · {product.name}",
            product_id=product_id,
        )
        self.active.add(product_id)
        return run

    async def execute(
        self, run: RunLogger, product_id: int, offer_ids: list[int] | None = None
    ) -> None:
        try:
            summary = await monitor.check_product(product_id, run, offer_ids)
            run.finish(summary=summary)
        except Exception as exc:
            log.exception("Check run %s failed", run.run_id)
            run.log("error", f"The check stopped unexpectedly: {exc}", level="error")
            run.finish("failed", error=str(exc))
        finally:
            self.active.discard(product_id)


scheduler = Scheduler()
