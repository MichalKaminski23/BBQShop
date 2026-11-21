"""Endpointy modułu Race Conditions."""

from fastapi import APIRouter, HTTPException, status

from bbq_core.deps import SessionDep
from bbq_core.module import Variant
from bbq_race.repository import CouponRepository, reset_demo_coupon
from bbq_race.schemas import CouponOut, RedeemRequest, RedemptionOut
from bbq_race.secure import SecureCouponRepository
from bbq_race.vulnerable import VulnerableCouponRepository

REPOSITORIES: dict[Variant, type[CouponRepository]] = {
    Variant.VULNERABLE: VulnerableCouponRepository,
    Variant.SECURE: SecureCouponRepository,
}


def build_router(variant: Variant) -> APIRouter:
    repository_cls = REPOSITORIES[variant]
    router = APIRouter(prefix="/race/coupons", tags=["race"])

    @router.get("/{code}", response_model=CouponOut)
    async def get_coupon(code: str, session: SessionDep) -> CouponOut:
        coupon = await repository_cls(session).get(code)
        if coupon is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kupon nie istnieje.")
        return coupon

    @router.post("/redeem", response_model=RedemptionOut)
    async def redeem_coupon(payload: RedeemRequest, session: SessionDep) -> RedemptionOut:
        repository = repository_cls(session)
        coupon = await repository.redeem(payload.code)
        if coupon is not None:
            return coupon
        if await repository.get(payload.code) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kupon nie istnieje.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Kupon został już wykorzystany."
        )

    @router.post("/reset", response_model=CouponOut)
    async def reset_coupon(session: SessionDep) -> CouponOut:
        """Resetuj wyłącznie kupon demonstracyjny GRILL10."""
        coupon = await reset_demo_coupon(session)
        if coupon is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kupon nie istnieje.")
        return coupon

    return router
