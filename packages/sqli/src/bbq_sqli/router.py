"""Endpointy modułu SQLi – implementacja zależy od wariantu z ``.env``."""

from typing import Annotated

from fastapi import APIRouter, Query

from bbq_core.deps import SessionDep
from bbq_core.module import Variant
from bbq_sqli.repository import ProductRepository
from bbq_sqli.schemas import ProductOut
from bbq_sqli.secure import MAX_QUERY_LENGTH, SecureProductRepository
from bbq_sqli.vulnerable import VulnerableProductRepository

REPOSITORIES: dict[Variant, type[ProductRepository]] = {
    Variant.VULNERABLE: VulnerableProductRepository,
    Variant.SECURE: SecureProductRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    max_length = MAX_QUERY_LENGTH if variant is Variant.SECURE else None

    router = APIRouter(prefix="/products", tags=["sqli"])

    @router.get("/search")
    async def search_products(
        session: SessionDep,
        q: Annotated[str, Query(max_length=max_length, description="Fraza w nazwie")] = "",
    ) -> list[ProductOut]:
        """Wyszukuje produkty po nazwie."""
        return await repository_cls(session).search(q)

    return router
