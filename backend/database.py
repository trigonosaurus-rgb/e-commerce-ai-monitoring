"""Database engine and sessions.

Request handlers get a session through the `SessionDep` dependency; background work
(agent runs, scheduled checks) opens short-lived sessions with `session_scope()`.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from alembic import command
from alembic.config import Config
from fastapi import Depends
from sqlalchemy import Engine, event, inspect
from sqlmodel import Session, create_engine

from backend import models  # noqa: F401  (registers tables on SQLModel.metadata)
from backend.config import ROOT_DIR, get_settings


@lru_cache
def get_engine() -> Engine:
    url = get_settings().database_url
    if url.startswith("sqlite:///"):
        Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")  # readers don't block the writer
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()

        return engine
    return create_engine(url, pool_pre_ping=True)


def init_db() -> None:
    """Brings the schema up to date by applying Alembic migrations (creates it on first run)."""
    engine = get_engine()
    config = Config(str(ROOT_DIR / "alembic.ini"))
    tables = set(inspect(engine).get_table_names())
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        if tables and "alembic_version" not in tables:
            # a database created before migrations existed: it already matches the first one
            command.stamp(config, "head")
        else:
            command.upgrade(config, "head")


@contextmanager
def session_scope() -> Iterator[Session]:
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
