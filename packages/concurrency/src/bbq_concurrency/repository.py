"""Wspólny interfejs obu wariantów składania zamówień."""

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from bbq_concurrency.schemas import CreateOrderResult, OrderCreate


class OrderRepository(Protocol):
    def __init__(self, session: AsyncSession) -> None: ...

    async def create_order(
        self, order_data: OrderCreate, idempotency_key: str | None
    ) -> CreateOrderResult:
        """Tworzy zamówienie albo zwraca wcześniej utworzone."""
        ...
