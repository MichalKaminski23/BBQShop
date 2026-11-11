"""Testy nagłówków diagnostycznych endpointu zamówień."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from bbq_api import create_app
from bbq_core.config import Settings
from bbq_core.module import Variant
from bbq_db.seed.data import ORDERS
from bbq_nplusone import module

pytestmark = pytest.mark.integration

type ClientFactory = Callable[[Variant], AbstractAsyncContextManager[httpx.AsyncClient]]


@pytest.fixture
def client_for(pg_engine: AsyncEngine, postgres_dsn: str, mongo_uri: str) -> ClientFactory:
    @asynccontextmanager
    async def factory(variant: Variant) -> AsyncIterator[httpx.AsyncClient]:
        settings = Settings(
            postgres_dsn=postgres_dsn,
            mongo_uri=mongo_uri,
            modules={"nplusone": variant},
            db_metrics=True,
        )
        app = create_app(settings, modules=[module])
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

    return factory


@pytest.mark.parametrize(
    ("variant", "expected_queries"),
    [
        (Variant.VULNERABLE, len(ORDERS) + 1),
        (Variant.SECURE, 2),
    ],
    ids=["vulnerable", "secure"],
)
async def test_orders_include_query_metrics(
    client_for: ClientFactory, variant: Variant, expected_queries: int
) -> None:
    async with client_for(variant) as client:
        response = await client.get("/api/orders")

    assert response.status_code == 200
    assert response.headers["X-SQL-Query-Count"] == str(expected_queries)
    assert float(response.headers["X-SQL-Query-Time-Ms"]) >= 0
