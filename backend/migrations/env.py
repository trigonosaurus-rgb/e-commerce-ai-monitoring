"""Alembic environment: uses the app's settings and SQLModel metadata.

The app runs migrations itself on startup (backend/database.py → init_db) and passes its
own connection in `config.attributes["connection"]`; the `alembic` CLI opens one here.
"""

from alembic import context
from sqlalchemy import Connection
from sqlmodel import SQLModel
from sqlmodel.sql.sqltypes import AutoString

from backend import models
from backend.database import get_engine

target_metadata = SQLModel.metadata


def render_item(type_, obj, autogen_context):
    """Writes our custom column types into migrations with correct imports."""
    if type_ == "type" and isinstance(obj, models.UTCDateTime):
        autogen_context.imports.add("import backend.models")
        return "backend.models.UTCDateTime()"
    if type_ == "type" and isinstance(obj, AutoString):
        autogen_context.imports.add("import sqlmodel")
        return "sqlmodel.sql.sqltypes.AutoString()"
    return False


def run(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # SQLite can't ALTER most things; batch mode recreates tables
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


if (shared := context.config.attributes.get("connection")) is not None:
    run(shared)
else:
    with get_engine().connect() as connection:
        run(connection)
