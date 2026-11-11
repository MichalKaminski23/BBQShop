"""Testy powtórnego i równoległego składania tego samego zamówienia."""

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from bbq_api import create_app
from bbq_concurrency import module
from bbq_core.config import Settings
from bbq_core.module import Variant
from bbq_db.models import Order

pytestmark = pytest.mark.integration

type ClientFactory = Callable[[Variant], AbstractAsyncContextManager[httpx.AsyncClient]]


@pytest.fixture
def client_for(pg_engine: AsyncEngine, postgres_dsn: str, mongo_uri: str) -> ClientFactory:
    @asynccontextmanager
    async def factory(variant: Variant) -> AsyncIterator[httpx.AsyncClient]:
        settings = Settings(
            postgres_dsn=postgres_dsn,
            mongo_uri=mongo_uri,
            modules={"concurrency": variant},
        )
        app = create_app(settings, modules=[module])
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

    return factory


@pytest.fixture(autouse=True)
async def remove_orders_created_by_test(pg_engine: AsyncEngine) -> AsyncIterator[None]:
    yield
    async with AsyncSession(pg_engine) as session:
        await session.execute(delete(Order).where(Order.customer_name.like("Concurrency test %")))
        await session.commit()


@pytest.mark.parametrize(
    ("variant", "expected_unique_orders"),
    [
        (Variant.VULNERABLE, 8),
        (Variant.SECURE, 1),
    ],
    ids=["vulnerable", "secure"],
)
async def test_repeated_concurrent_requests_create_one_or_many_orders(
    client_for: ClientFactory, variant: Variant, expected_unique_orders: int
) -> None:
    payload = {
        "customer_name": f"Concurrency test {uuid4()}",
        "items": [{"product_id": 1, "quantity": 1}],
    }
    key = str(uuid4())

    async with client_for(variant) as client:
        responses = await asyncio.gather(
            *(
                client.post(
                    "/api/orders",
                    json=payload,
                    headers={"Idempotency-Key": key},
                )
                for _ in range(8)
            )
        )

    assert all(response.status_code in {200, 201} for response in responses)
    order_ids = {response.json()["order"]["id"] for response in responses}
    assert len(order_ids) == expected_unique_orders


async def test_secure_requires_idempotency_key(client_for: ClientFactory) -> None:
    async with client_for(Variant.SECURE) as client:
        response = await client.post(
            "/api/orders",
            json={"customer_name": "Missing key", "items": [{"product_id": 1, "quantity": 1}]},
        )

    assert response.status_code == 422
