"""Te same scenariusze uruchamiane na obu wariantach wyszukiwarki."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_db.seed.data import PRODUCTS, SECRETS
from bbq_sqli.repository import ProductRepository
from bbq_sqli.secure import SecureProductRepository
from bbq_sqli.vulnerable import VulnerableProductRepository

pytestmark = pytest.mark.integration

BOTH = pytest.mark.parametrize(
    "repository_cls",
    [VulnerableProductRepository, SecureProductRepository],
    ids=["vulnerable", "secure"],
)

UNION_PAYLOAD = "' UNION SELECT id, name, 'leak', 0, value FROM admin_secrets--"
SECRET_VALUES = {str(secret["value"]) for secret in SECRETS}


@BOTH
async def test_search_finds_products_by_name(
    db_session: AsyncSession, repository_cls: type[ProductRepository]
) -> None:
    results = await repository_cls(db_session).search("grill")

    assert results
    assert all("grill" in product.name.lower() for product in results)


@BOTH
async def test_empty_query_returns_all_products(
    db_session: AsyncSession, repository_cls: type[ProductRepository]
) -> None:
    results = await repository_cls(db_session).search("")

    assert len(results) == len(PRODUCTS)


async def test_union_payload_leaks_secrets_in_vulnerable(db_session: AsyncSession) -> None:
    results = await VulnerableProductRepository(db_session).search(UNION_PAYLOAD)

    leaked = {product.description for product in results}
    assert leaked >= SECRET_VALUES


async def test_union_payload_is_plain_text_in_secure(db_session: AsyncSession) -> None:
    results = await SecureProductRepository(db_session).search(UNION_PAYLOAD)

    assert results == []


async def test_like_wildcards_are_literal_in_secure(db_session: AsyncSession) -> None:
    assert await SecureProductRepository(db_session).search("%") == []
    assert await SecureProductRepository(db_session).search("_") == []
