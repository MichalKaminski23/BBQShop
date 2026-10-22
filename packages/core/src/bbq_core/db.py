"""Połączenia z PostgreSQL (SQLAlchemy async) i MongoDB (PyMongo async)."""

from pymongo import AsyncMongoClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(dsn: str) -> AsyncEngine:
    """Tworzy silnik PostgreSQL z pulą połączeń."""
    return create_async_engine(dsn, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Tworzy fabrykę sesji ORM."""
    return async_sessionmaker(engine, expire_on_commit=False)


def create_mongo_client(uri: str) -> AsyncMongoClient[dict[str, object]]:
    """Tworzy klienta MongoDB (połączenie jest nawiązywane leniwie)."""
    return AsyncMongoClient(uri, tz_aware=True)
