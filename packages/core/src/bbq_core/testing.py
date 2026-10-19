"""Fixtures pytest współdzielone przez wszystkie moduły (plugin ładowany w ``conftest.py``).

Bazy danych startują jako kontenery Dockera (testcontainers) raz na sesję testów.
Każdy test dostaje sesję w transakcji, która jest wycofywana po teście.
"""

from collections.abc import AsyncIterator, Iterator
from importlib.metadata import entry_points

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from testcontainers.community.mongodb import MongoDbContainer
from testcontainers.community.postgres import PostgresContainer

from bbq_core.db import Base, create_engine
from bbq_core.module import ENTRY_POINT_GROUP

POSTGRES_IMAGE = "postgres:17-alpine"
MONGO_IMAGE = "mongo:8"


@pytest.fixture(scope="session")
def postgres_dsn() -> Iterator[str]:
    with PostgresContainer(POSTGRES_IMAGE, driver="asyncpg") as container:
        yield container.get_connection_url()


@pytest.fixture(scope="session")
def mongo_uri() -> Iterator[str]:
    with MongoDbContainer(MONGO_IMAGE) as container:
        yield container.get_connection_url()


@pytest.fixture(scope="session")
async def pg_engine(postgres_dsn: str) -> AsyncIterator[AsyncEngine]:
    """Silnik z utworzonymi tabelami wszystkich zainstalowanych modułów."""
    for entry_point in entry_points(group=ENTRY_POINT_GROUP):
        entry_point.load()  # rejestruje modele w Base.metadata

    engine = create_engine(postgres_dsn)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(pg_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Sesja, której zmiany są wycofywane po teście."""
    async with pg_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
