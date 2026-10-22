"""Wypełnianie baz danymi przykładowymi. Każda funkcja jest idempotentna."""

from pymongo.asynchronous.database import AsyncDatabase
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_db.base import Base
from bbq_db.models import AdminSecret, Coupon, Order, OrderItem, Product
from bbq_db.mongo.users import USERS_COLLECTION, hash_password
from bbq_db.seed.data import COUPONS, ORDERS, PRODUCTS, SECRETS, USERS


async def _is_empty(session: AsyncSession, model: type[Base]) -> bool:
    return not await session.scalar(select(exists().select_from(model)))


async def seed_postgres(session: AsyncSession) -> None:
    """Wstawia produkty, sekrety, kupony i zamówienia do pustych tabel."""
    if await _is_empty(session, Product):
        session.add_all(Product(**data) for data in PRODUCTS)
    if await _is_empty(session, AdminSecret):
        session.add_all(AdminSecret(**data) for data in SECRETS)
    if await _is_empty(session, Coupon):
        session.add_all(Coupon(**data) for data in COUPONS)
    await session.flush()

    if await _is_empty(session, Order):
        products = {p.name: p for p in await session.scalars(select(Product))}
        for customer, lines in ORDERS:
            items = [
                OrderItem(product=products[name], quantity=qty, unit_price=products[name].price)
                for name, qty in lines
            ]
            session.add(Order(customer_name=customer, items=items))
        await session.flush()


async def seed_mongo(db: AsyncDatabase[dict[str, object]]) -> None:
    """Tworzy indeks i użytkowników w pustej kolekcji ``users``."""
    users = db[USERS_COLLECTION]
    await users.create_index("username", unique=True)
    if await users.count_documents({}, limit=1) == 0:
        await users.insert_many(
            {"username": name, "password_hash": hash_password(password), "role": role}
            for name, password, role in USERS
        )
