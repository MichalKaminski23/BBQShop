"""Wersja POPRAWIONA - idempotencja i limit równoległych operacji."""

import asyncio

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bbq_concurrency.schemas import CreateOrderResult, OrderCreate, OrderItemOut, OrderOut
from bbq_db.models import Order, OrderItem, Product

MAX_CONCURRENT_ORDERS = 4
_ORDER_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_ORDERS)


class SecureOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_order(
        self, order_data: OrderCreate, idempotency_key: str | None
    ) -> CreateOrderResult:
        if idempotency_key is None:
            raise ValueError("Idempotency-Key jest wymagany.")

        async with _ORDER_SEMAPHORE:
            existing = await self._find_by_key(idempotency_key)
            if existing is not None:
                return CreateOrderResult(order=self._to_output(existing), created=False)

            items = await self._build_items(order_data)
            order = Order(
                customer_name=order_data.customer_name,
                idempotency_key=idempotency_key,
                items=items,
            )
            self._session.add(order)
            try:
                await self._session.commit()
            except IntegrityError:
                await self._session.rollback()
                existing = await self._find_by_key(idempotency_key)
                if existing is None:
                    raise
                return CreateOrderResult(order=self._to_output(existing), created=False)

            return CreateOrderResult(order=self._to_output(order), created=True)

    async def _find_by_key(self, idempotency_key: str) -> Order | None:
        return await self._session.scalar(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.idempotency_key == idempotency_key)
        )

    async def _build_items(self, order_data: OrderCreate) -> list[OrderItem]:
        product_ids = {item.product_id for item in order_data.items}
        products = {
            product.id: product
            for product in await self._session.scalars(
                select(Product).where(Product.id.in_(product_ids))
            )
        }
        if len(products) != len(product_ids):
            raise LookupError("Co najmniej jeden produkt nie istnieje.")
        return [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=products[item.product_id].price,
            )
            for item in order_data.items
        ]

    @staticmethod
    def _to_output(order: Order) -> OrderOut:
        return OrderOut(
            id=order.id,
            customer_name=order.customer_name,
            created_at=order.created_at,
            items=[OrderItemOut.model_validate(item) for item in order.items],
        )
