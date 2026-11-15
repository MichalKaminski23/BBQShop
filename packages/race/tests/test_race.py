"""Testy repozytorium i API dla wariantów modułu Race."""

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

import httpx
import pytest
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from bbq_api import create_app
from bbq_core.config import Settings
from bbq_core.module import Variant
from bbq_db.models import Coupon
from bbq_race import module as race_module
from bbq_race.secure import SecureCouponRepository
from bbq_race.vulnerable import VulnerableCouponRepository

pytestmark = pytest.mark.integration

type ClientFactory = Callable[[Variant], AbstractAsyncContextManager[httpx.AsyncClient]]


@pytest.fixture
def client_for(pg_engine: AsyncEngine, postgres_dsn: str, mongo_uri: str) -> ClientFactory:
    @asynccontextmanager
    async def factory(variant: Variant) -> AsyncIterator[httpx.AsyncClient]:
        settings = Settings(
            postgres_dsn=postgres_dsn, mongo_uri=mongo_uri, modules={"race": variant}
        )
        app = create_app(settings, modules=[race_module])
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client,
        ):
            yield client

    return factory


async def reset_coupon(engine: AsyncEngine) -> None:
    async with AsyncSession(engine) as session:
        await session.execute(update(Coupon).where(Coupon.code == "GRILL10").values(uses_left=1))
        await session.commit()


@pytest.mark.parametrize("variant", [Variant.VULNERABLE, Variant.SECURE])
async def test_get_and_sequential_redeem(
    client_for: ClientFactory, pg_engine: AsyncEngine, variant: Variant
) -> None:
    await reset_coupon(pg_engine)
    async with client_for(variant) as client:
        info = await client.get("/api/race/coupons/GRILL10")
        first = await client.post("/api/race/coupons/redeem", json={"code": "GRILL10"})
        second = await client.post("/api/race/coupons/redeem", json={"code": "GRILL10"})
        missing = await client.get("/api/race/coupons/UNKNOWN")

    assert info.status_code == 200 and info.json()["uses_left"] == 1
    assert first.status_code == 200 and first.json()["discount_percent"] == 10
    assert second.status_code == 409
    assert missing.status_code == 404


async def test_secure_concurrent_redemption_is_atomic(pg_engine: AsyncEngine) -> None:
    await reset_coupon(pg_engine)

    async def redeem() -> bool:
        async with AsyncSession(pg_engine, expire_on_commit=False) as session:
            return await SecureCouponRepository(session).redeem("GRILL10") is not None

    results = await asyncio.gather(*(redeem() for _ in range(20)))
    assert sum(results) == 1


async def test_vulnerable_concurrent_redemption_exceeds_limit(pg_engine: AsyncEngine) -> None:
    await reset_coupon(pg_engine)

    async def redeem() -> bool:
        async with AsyncSession(pg_engine, expire_on_commit=False) as session:
            return await VulnerableCouponRepository(session).redeem("GRILL10") is not None

    results = await asyncio.gather(*(redeem() for _ in range(20)))
    assert sum(results) > 1


async def test_off_does_not_register_endpoints(client_for: ClientFactory) -> None:
    async with client_for(Variant.OFF) as client:
        response = await client.get("/api/race/coupons/GRILL10")

    assert response.status_code == 404


async def test_demo_reset_changes_only_grill10(
    client_for: ClientFactory, pg_engine: AsyncEngine
) -> None:
    async with AsyncSession(pg_engine) as session:
        await session.execute(update(Coupon).where(Coupon.code == "GRILL10").values(uses_left=0))
        await session.execute(update(Coupon).where(Coupon.code == "LATO2026").values(uses_left=23))
        await session.commit()

    async with client_for(Variant.SECURE) as client:
        response = await client.post("/api/race/coupons/reset")

    assert response.status_code == 200
    assert response.json()["uses_left"] == 1
    async with AsyncSession(pg_engine) as session:
        rows = {coupon.code: coupon.uses_left for coupon in await session.scalars(select(Coupon))}

    assert rows["GRILL10"] == 1
    assert rows["LATO2026"] == 23


async def test_coupon_reset_changes_only_target_coupon(pg_engine: AsyncEngine) -> None:
    async with AsyncSession(pg_engine) as session:
        await session.execute(update(Coupon).values(uses_left=23))
        await session.commit()
    await reset_coupon(pg_engine)
    async with AsyncSession(pg_engine) as session:
        rows = {coupon.code: coupon.uses_left for coupon in await session.scalars(select(Coupon))}

    assert rows["GRILL10"] == 1
    assert rows["LATO2026"] == 23
