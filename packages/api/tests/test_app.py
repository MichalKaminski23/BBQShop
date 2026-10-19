"""Testy aplikacji złożonej z modułów: rejestr, endpointy systemowe, przełączanie wariantów."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from bbq_api import create_app
from bbq_api.registry import discover_modules
from bbq_core.config import Settings
from bbq_core.module import Variant
from bbq_sqli import module as sqli_module

pytestmark = pytest.mark.integration

UNION_PAYLOAD = "' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--"

type ClientFactory = Callable[[Variant], AbstractAsyncContextManager[httpx.AsyncClient]]


@pytest.fixture
def client_for(pg_engine: AsyncEngine, postgres_dsn: str, mongo_uri: str) -> ClientFactory:
    """Tworzy klienta HTTP do aplikacji z modułem SQLi w wybranym wariancie."""

    @asynccontextmanager
    async def factory(variant: Variant) -> AsyncIterator[httpx.AsyncClient]:
        settings = Settings(
            postgres_dsn=postgres_dsn,
            mongo_uri=mongo_uri,
            modules={"sqli": variant},
        )
        app = create_app(settings, modules=[sqli_module])
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

    return factory


def test_sqli_module_is_discovered_via_entry_point() -> None:
    assert "sqli" in {module.name for module in discover_modules()}


async def test_health_reports_both_databases(client_for: ClientFactory) -> None:
    async with client_for(Variant.SECURE) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"postgres": "ok", "mongo": "ok"}


@pytest.mark.parametrize("variant", list(Variant))
async def test_modules_endpoint_reports_variant(
    client_for: ClientFactory, variant: Variant
) -> None:
    async with client_for(variant) as client:
        response = await client.get("/api/modules")

    assert response.json() == [
        {
            "name": "sqli",
            "title": sqli_module.title,
            "description": sqli_module.description,
            "variant": variant.value,
        }
    ]


async def test_module_off_is_not_mounted(client_for: ClientFactory) -> None:
    async with client_for(Variant.OFF) as client:
        response = await client.get("/api/products/search")

    assert response.status_code == 404


async def test_union_payload_leaks_only_in_vulnerable(client_for: ClientFactory) -> None:
    async with client_for(Variant.VULNERABLE) as client:
        vulnerable = await client.get("/api/products/search", params={"q": UNION_PAYLOAD})
    async with client_for(Variant.SECURE) as client:
        secure = await client.get("/api/products/search", params={"q": UNION_PAYLOAD})

    assert any(p["category"] == "leak" for p in vulnerable.json())
    assert secure.status_code == 200
    assert secure.json() == []


async def test_secure_rejects_too_long_query(client_for: ClientFactory) -> None:
    async with client_for(Variant.SECURE) as client:
        response = await client.get("/api/products/search", params={"q": "x" * 101})

    assert response.status_code == 422
