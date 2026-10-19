"""Migracje Alembica tworzą schemat zgodny z modelami ORM."""

import asyncio
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.engine import Connection, make_url

from bbq_core.config import get_settings
from bbq_core.db import Base, create_engine

pytestmark = pytest.mark.integration

ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


async def _recreate_database(dsn: str, name: str) -> None:
    engine = create_engine(dsn).execution_options(isolation_level="AUTOCOMMIT")
    async with engine.connect() as connection:
        await connection.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        await connection.execute(text(f'CREATE DATABASE "{name}"'))
    await engine.dispose()


async def _schema_diff(dsn: str) -> list[object]:
    def compare(connection: Connection) -> list[object]:
        return list(compare_metadata(MigrationContext.configure(connection), Base.metadata))

    engine = create_engine(dsn)
    async with engine.connect() as connection:
        diff = await connection.run_sync(compare)
    await engine.dispose()
    return diff


def test_migrations_match_models(postgres_dsn: str, monkeypatch: pytest.MonkeyPatch) -> None:
    migrations_dsn = make_url(postgres_dsn).set(database="migrations_test")
    dsn = migrations_dsn.render_as_string(hide_password=False)
    asyncio.run(_recreate_database(postgres_dsn, "migrations_test"))

    monkeypatch.setenv("BBQ_POSTGRES_DSN", dsn)
    get_settings.cache_clear()
    try:
        command.upgrade(Config(str(ALEMBIC_INI)), "head")
    finally:
        get_settings.cache_clear()

    assert asyncio.run(_schema_diff(dsn)) == []
