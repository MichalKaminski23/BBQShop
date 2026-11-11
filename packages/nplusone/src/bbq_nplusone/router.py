"""Endpointy modułu N+1 – implementacja zależy od wariantu z ``.env``."""

from fastapi import APIRouter

from bbq_core.deps import SessionDep
from bbq_core.module import Variant
from bbq_nplusone.repository import OrderRepository
from bbq_nplusone.schemas import OrderOut
from bbq_nplusone.secure import SecureOrderRepository
from bbq_nplusone.vulnerable import VulnerableOrderRepository

REPOSITORIES: dict[Variant, type[OrderRepository]] = {
    Variant.VULNERABLE: VulnerableOrderRepository,
    Variant.SECURE: SecureOrderRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    router = APIRouter(prefix="/orders", tags=["nplusone"])

    @router.get("")
    async def list_orders(session: SessionDep) -> list[OrderOut]:
        """Zwraca zamówienia wraz z ich pozycjami."""
        return await repository_cls(session).list_orders()

    return router
