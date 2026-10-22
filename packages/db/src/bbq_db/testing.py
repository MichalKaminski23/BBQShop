"""Fixtures pytest współdzielone przez wszystkie moduły (plugin ładowany w ``conftest.py``).

Bazy danych startują jako kontenery Dockera (testcontainers) raz na sesję testów
i są od razu wypełniane danymi przykładowymi. Każdy test dostaje sesję w transakcji,
która jest wycofywana po teście, więc testy nie wpływają na siebie nawzajem.
"""

from collections.abc import AsyncIterator, Iterator

import pytest
from pymongo.asynchronous.database import AsyncDatabase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from testcontainers.community.mongodb import MongoDbContainer
from testcontainers.community.postgres import PostgresContainer

from bbq_core.db import create_engine, create_mongo_client
from bbq_db.base import Base
from bbq_db.seed import seed_mongo, seed_postgres

POSTGRES_IMAGE = "postgres:17-alpine"
MONGO_IMAGE = "mongo:8"
MONGO_TEST_DB = "bbqshop_test"


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
    """Silnik z utworzonym schematem i danymi przykładowymi."""
    engine = create_engine(postgres_dsn)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        await seed_postgres(session)
        await session.commit()
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


@pytest.fixture(scope="session")
async def mongo_db(mongo_uri: str) -> AsyncIterator[AsyncDatabase[dict[str, object]]]:
    """Baza MongoDB z danymi przykładowymi."""
    client = create_mongo_client(mongo_uri)
    db = client[MONGO_TEST_DB]
    await seed_mongo(db)
    yield db
    await client.close()
