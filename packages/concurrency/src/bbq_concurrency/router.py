"""Endpoint składania zamówień zależny od wariantu z ``.env``."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from bbq_concurrency.repository import OrderRepository
from bbq_concurrency.schemas import CreateOrderResult, OrderCreate
from bbq_concurrency.secure import SecureOrderRepository
from bbq_concurrency.vulnerable import VulnerableOrderRepository
from bbq_core.deps import SessionDep
from bbq_core.module import Variant

REPOSITORIES: dict[Variant, type[OrderRepository]] = {
    Variant.VULNERABLE: VulnerableOrderRepository,
    Variant.SECURE: SecureOrderRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    router = APIRouter(prefix="/orders", tags=["concurrency"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    async def create_order(
        order_data: OrderCreate,
        session: SessionDep,
        response: Response,
        idempotency_key: Annotated[
            str | None, Header(max_length=64, description="Klucz powtórzenia operacji")
        ] = None,
    ) -> CreateOrderResult:
        """Składa zamówienie, opcjonalnie chroniąc je kluczem idempotencji."""
        if variant is Variant.SECURE and idempotency_key is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Nagłówek Idempotency-Key jest wymagany.",
            )

        try:
            result = await repository_cls(session).create_order(order_data, idempotency_key)
        except LookupError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

        if not result.created:
            response.status_code = status.HTTP_200_OK
        return result

    return router
