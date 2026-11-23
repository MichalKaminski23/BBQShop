"""Wersja PODATNA - celowo wykonuje zapytanie pozycji dla każdego zamówienia."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_db.models import Order, OrderItem
from bbq_nplusone.schemas import OrderItemOut, OrderOut


class VulnerableOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(self, customer_name: str | None = None) -> list[OrderOut]:
        stmt = select(Order)
        if customer_name is not None:
            stmt = stmt.where(Order.customer_name == customer_name)
        orders = await self._session.scalars(stmt.order_by(Order.id))
        result: list[OrderOut] = []
        for order in orders:
            items = await self._session.scalars(
                select(OrderItem).where(OrderItem.order_id == order.id).order_by(OrderItem.id)
            )
            result.append(
                OrderOut(
                    id=order.id,
                    customer_name=order.customer_name,
                    created_at=order.created_at,
                    items=[OrderItemOut.model_validate(item) for item in items],
                )
            )
        return result
