"""Połączenia z PostgreSQL (SQLAlchemy async) i MongoDB (PyMongo async)."""

import contextvars
import time
from dataclasses import dataclass
from typing import Protocol, cast

from pymongo import AsyncMongoClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@dataclass
class QueryMetrics:
    """Metryki zapytań SQL wykonywanych w bieżącym żądaniu."""

    count: int = 0
    elapsed_ms: float = 0.0


_query_metrics: contextvars.ContextVar[QueryMetrics | None] = contextvars.ContextVar(
    "bbq_query_metrics", default=None
)


class _ExecutionContext(Protocol):
    _bbq_query_started: float


def begin_query_metrics() -> tuple[QueryMetrics, contextvars.Token[QueryMetrics | None]]:
    """Rozpoczyna zbieranie metryk zapytań dla bieżącego kontekstu."""
    metrics = QueryMetrics()
    token = _query_metrics.set(metrics)
    return metrics, token


def end_query_metrics(token: contextvars.Token[QueryMetrics | None]) -> None:
    """Kończy zbieranie metryk i przywraca poprzedni kontekst."""
    _query_metrics.reset(token)


def create_engine(dsn: str, *, enable_metrics: bool = False) -> AsyncEngine:
    """Tworzy silnik PostgreSQL z pulą połączeń."""
    engine = create_async_engine(dsn, echo=enable_metrics, pool_pre_ping=True)
    if enable_metrics:
        _install_query_metrics(engine)
    return engine


def _install_query_metrics(engine: AsyncEngine) -> None:
    """Podłącza pomiar czasu i liczby zapytań do silnika."""
    sync_engine = engine.sync_engine

    @event.listens_for(sync_engine, "before_cursor_execute")
    def before_cursor_execute(
        _connection: object,
        _cursor: object,
        _statement: str,
        _parameters: object,
        context: object,
        _executemany: bool,
    ) -> None:
        execution_context = cast(_ExecutionContext, context)
        execution_context._bbq_query_started = time.perf_counter()

    @event.listens_for(sync_engine, "after_cursor_execute")
    def after_cursor_execute(
        _connection: object,
        _cursor: object,
        _statement: str,
        _parameters: object,
        context: object,
        _executemany: bool,
    ) -> None:
        metrics = _query_metrics.get()
        started = getattr(context, "_bbq_query_started", None)
        if metrics is not None and isinstance(started, float):
            metrics.count += 1
            metrics.elapsed_ms += (time.perf_counter() - started) * 1000


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Tworzy fabrykę sesji ORM."""
    return async_sessionmaker(engine, expire_on_commit=False)


def create_mongo_client(uri: str) -> AsyncMongoClient[dict[str, object]]:
    """Tworzy klienta MongoDB (połączenie jest nawiązywane leniwie)."""
    return AsyncMongoClient(uri, tz_aware=True)
