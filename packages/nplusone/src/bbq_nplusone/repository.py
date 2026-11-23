"""Wspólny interfejs obu wariantów listy zamówień."""

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from bbq_nplusone.schemas import OrderOut


class OrderRepository(Protocol):
    def __init__(self, session: AsyncSession) -> None: ...

    async def list_orders(self, customer_name: str | None = None) -> list[OrderOut]:
        """Zwraca zamówienia, opcjonalnie filtrowane po kliencie."""
        ...
