"""Wersja POPRAWIONA - pozycje wszystkich zamówień są ładowane zbiorczo."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bbq_db.models import Order
from bbq_nplusone.schemas import OrderOut


class SecureOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(self) -> list[OrderOut]:
        stmt = select(Order).options(selectinload(Order.items)).order_by(Order.id)
        orders = await self._session.scalars(stmt)
        return [OrderOut.model_validate(order) for order in orders]
