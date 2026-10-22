"""Dane przykładowe trafiają do obu baz i nie dublują się przy ponownym uruchomieniu."""

import pytest
from pymongo.asynchronous.database import AsyncDatabase
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bbq_db.models import AdminSecret, Coupon, Order, Product
from bbq_db.mongo import USERS_COLLECTION, verify_password
from bbq_db.seed import seed_mongo, seed_postgres
from bbq_db.seed.data import COUPONS, ORDERS, PRODUCTS, SECRETS, USERS

pytestmark = pytest.mark.integration


async def _count(session: AsyncSession, model: type[object]) -> int:
    return await session.scalar(select(func.count()).select_from(model)) or 0


async def test_postgres_seed_is_complete_and_idempotent(db_session: AsyncSession) -> None:
    await seed_postgres(db_session)  # drugi raz – nic nie powinno się zdublować

    assert await _count(db_session, Product) == len(PRODUCTS)
    assert await _count(db_session, AdminSecret) == len(SECRETS)
    assert await _count(db_session, Coupon) == len(COUPONS)
    assert await _count(db_session, Order) == len(ORDERS)


async def test_orders_have_items_with_product_prices(db_session: AsyncSession) -> None:
    orders = await db_session.scalars(select(Order).options(selectinload(Order.items)))

    for order in orders:
        assert order.items
        for item in order.items:
            product = await db_session.get_one(Product, item.product_id)
            assert item.unit_price == product.price


async def test_mongo_users_have_hashed_passwords(
    mongo_db: AsyncDatabase[dict[str, object]],
) -> None:
    await seed_mongo(mongo_db)  # drugi raz – bez duplikatów

    users = {u["username"]: u async for u in mongo_db[USERS_COLLECTION].find()}

    assert set(users) == {name for name, _, _ in USERS}
    for name, password, _ in USERS:
        stored = str(users[name]["password_hash"])
        assert password not in stored
        assert verify_password(password, stored)
        assert not verify_password("wrong", stored)
