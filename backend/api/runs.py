"""Agent activity (runs + their event journal) and alerts."""

from fastapi import APIRouter
from sqlmodel import Session, col, func, select

from backend.api.schemas import AlertOut, EventOut, RunOut
from backend.auth import Workspace, WorkspaceDep, api_error
from backend.database import SessionDep
from backend.models import Alert, Product, Run, RunEvent

router = APIRouter(tags=["activity"])


def owned_run(session: Session, ws: Workspace, run_id: int) -> Run:
    run = session.get(Run, run_id)
    if run is None or run.user_id != ws.user.id:
        raise api_error(404, "not_found", "Run not found.")
    return run


def _with_names(session: Session, runs: list[Run]) -> list[RunOut]:
    ids = {r.product_id for r in runs if r.product_id}
    names = dict(
        session.exec(select(Product.id, Product.name).where(col(Product.id).in_(ids))).all()
    )
    return [
        RunOut.model_validate(r.model_dump() | {"product_name": names.get(r.product_id)})
        for r in runs
    ]


@router.get("/runs", response_model=list[RunOut])
def list_runs(
    ws: WorkspaceDep,
    session: SessionDep,
    product_id: int | None = None,
    kind: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    query = select(Run).where(Run.user_id == ws.user.id)
    if product_id is not None:
        query = query.where(Run.product_id == product_id)
    if kind:
        query = query.where(Run.kind == kind)
    runs = session.exec(
        query.order_by(col(Run.started_at).desc()).offset(offset).limit(min(limit, 200))
    ).all()
    return _with_names(session, list(runs))


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, ws: WorkspaceDep, session: SessionDep):
    return _with_names(session, [owned_run(session, ws, run_id)])[0]


@router.get("/runs/{run_id}/events", response_model=list[EventOut])
def run_events(run_id: int, ws: WorkspaceDep, session: SessionDep, after: int = 0):
    """The UI polls this with the last `seq` it has, so it only receives new events."""
    owned_run(session, ws, run_id)
    return session.exec(
        select(RunEvent)
        .where(RunEvent.run_id == run_id, RunEvent.seq > after)
        .order_by(col(RunEvent.seq))
    ).all()


@router.get("/alerts")
def list_alerts(ws: WorkspaceDep, session: SessionDep, limit: int = 50):
    alerts = session.exec(
        select(Alert)
        .where(Alert.user_id == ws.user.id)
        .order_by(col(Alert.created_at).desc())
        .limit(min(limit, 200))
    ).all()
    unread = session.exec(
        select(func.count()).where(Alert.user_id == ws.user.id, col(Alert.read).is_(False))
    ).one()
    return {
        "items": [AlertOut.model_validate(a, from_attributes=True) for a in alerts],
        "unread": unread,
    }


@router.post("/alerts/{alert_id}/read", status_code=204)
def mark_read(alert_id: int, ws: WorkspaceDep, session: SessionDep):
    ws.require_write()
    alert = session.get(Alert, alert_id)
    if alert is None or alert.user_id != ws.user.id:
        raise api_error(404, "not_found", "Alert not found.")
    alert.read = True
    session.commit()


@router.post("/alerts/read-all", status_code=204)
def mark_all_read(ws: WorkspaceDep, session: SessionDep):
    ws.require_write()
    for alert in session.exec(
        select(Alert).where(Alert.user_id == ws.user.id, col(Alert.read).is_(False))
    ):
        alert.read = True
    session.commit()
