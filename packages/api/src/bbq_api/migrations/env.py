"""Środowisko Alembica: metadane wszystkich modułów + async silnik z konfiguracji."""

import asyncio

from alembic import context
from sqlalchemy.engine import Connection

from bbq_api.registry import discover_modules
from bbq_core.config import get_settings
from bbq_core.db import Base, create_engine

# Import modułów rejestruje ich modele ORM w Base.metadata.
discover_modules()
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().postgres_dsn,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_sync(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_engine(get_settings().postgres_dsn)
    async with engine.connect() as connection:
        await connection.run_sync(_run_sync)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
