"""Logowanie przez HTTP: udane logowanie, bypass operatorem i walidacja wariantu poprawionego."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from bbq_api import create_app
from bbq_core.config import Settings
from bbq_core.module import Variant
from bbq_nosqli import module as nosqli_module

pytestmark = pytest.mark.integration

INJECTION: dict[str, Any] = {"username": {"$ne": None}, "password": {"$ne": None}}

type ClientFactory = Callable[[Variant], AbstractAsyncContextManager[httpx.AsyncClient]]


@pytest.fixture
def client_for(pg_engine: AsyncEngine, postgres_dsn: str, mongo_uri: str) -> ClientFactory:
    """Tworzy klienta HTTP do aplikacji z modułem NoSQLi w wybranym wariancie."""

    @asynccontextmanager
    async def factory(variant: Variant) -> AsyncIterator[httpx.AsyncClient]:
        settings = Settings(
            postgres_dsn=postgres_dsn,
            mongo_uri=mongo_uri,
            modules={"nosqli": variant},
        )
        app = create_app(settings, modules=[nosqli_module])
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

    return factory


async def test_valid_login_succeeds(client_for: ClientFactory) -> None:
    async with client_for(Variant.SECURE) as client:
        response = await client.post(
            "/api/login", json={"username": "admin", "password": "Admin123!"}
        )

    assert response.status_code == 200
    assert response.json() == {"username": "admin", "role": "admin"}


async def test_operator_injection_bypasses_login_only_in_vulnerable(
    client_for: ClientFactory,
) -> None:
    async with client_for(Variant.VULNERABLE) as client:
        vulnerable = await client.post("/api/login", json=INJECTION)
    async with client_for(Variant.SECURE) as client:
        secure = await client.post("/api/login", json=INJECTION)

    assert vulnerable.status_code == 200
    assert vulnerable.json()["role"] == "admin"
    assert secure.status_code == 422  # Pydantic odrzuca nie-tekstowe dane


async def test_wrong_password_is_rejected_in_both(client_for: ClientFactory) -> None:
    for variant in (Variant.VULNERABLE, Variant.SECURE):
        async with client_for(variant) as client:
            response = await client.post(
                "/api/login", json={"username": "admin", "password": "zle"}
            )

        assert response.status_code == 401


async def test_malformed_json_returns_400_in_vulnerable(client_for: ClientFactory) -> None:
    async with client_for(Variant.VULNERABLE) as client:
        response = await client.post(
            "/api/login", content="to nie jest json", headers={"Content-Type": "application/json"}
        )

    assert response.status_code == 400


async def test_non_object_body_returns_400_in_vulnerable(client_for: ClientFactory) -> None:
    async with client_for(Variant.VULNERABLE) as client:
        response = await client.post("/api/login", json=[1, 2, 3])

    assert response.status_code == 400
