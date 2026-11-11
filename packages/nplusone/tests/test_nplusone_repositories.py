"""Testy porównujące liczbę zapytań w obu wariantach modułu N+1."""

from collections.abc import Callable

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from bbq_db.seed.data import ORDERS
from bbq_nplusone.repository import OrderRepository
from bbq_nplusone.secure import SecureOrderRepository
from bbq_nplusone.vulnerable import VulnerableOrderRepository

pytestmark = pytest.mark.integration

BOTH = pytest.mark.parametrize(
    "repository_cls",
    [VulnerableOrderRepository, SecureOrderRepository],
    ids=["vulnerable", "secure"],
)


def count_queries(engine: AsyncEngine) -> tuple[list[str], Callable[[], None]]:
    statements: list[str] = []

    def before_cursor_execute(
        _conn: object,
        _cursor: object,
        statement: str,
        _parameters: object,
        _context: object,
        _executemany: bool,
    ) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", before_cursor_execute)

    def stop() -> None:
        event.remove(engine.sync_engine, "before_cursor_execute", before_cursor_execute)

    return statements, stop


@BOTH
async def test_list_orders_returns_items(
    db_session: AsyncSession, repository_cls: type[OrderRepository]
) -> None:
    orders = await repository_cls(db_session).list_orders()

    assert len(orders) == len(ORDERS)
    assert all(order.items for order in orders)


async def test_secure_variant_uses_two_queries(
    db_session: AsyncSession, pg_engine: AsyncEngine
) -> None:
    statements, stop = count_queries(pg_engine)
    try:
        orders = await SecureOrderRepository(db_session).list_orders()
    finally:
        stop()

    assert len(orders) == len(ORDERS)
    assert len(statements) == 2


async def test_vulnerable_variant_uses_one_query_per_order(
    db_session: AsyncSession, pg_engine: AsyncEngine
) -> None:
    statements, stop = count_queries(pg_engine)
    try:
        orders = await VulnerableOrderRepository(db_session).list_orders()
    finally:
        stop()

    assert len(orders) == len(ORDERS)
    assert len(statements) == len(ORDERS) + 1
