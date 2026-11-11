"""Wersja PODATNA – każde powtórzenie żądania tworzy nowe zamówienie."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_concurrency.schemas import CreateOrderResult, OrderCreate, OrderItemOut, OrderOut
from bbq_db.models import Order, OrderItem, Product


class VulnerableOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_order(
        self, order_data: OrderCreate, idempotency_key: str | None
    ) -> CreateOrderResult:
        del idempotency_key
        items = await self._build_items(order_data)
        order = Order(customer_name=order_data.customer_name, items=items)
        self._session.add(order)
        await self._session.commit()
        return CreateOrderResult(order=self._to_output(order), created=True)

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
