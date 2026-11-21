"""Implementacja celowo podatna na TOCTOU (check-then-act)."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_db.models import Coupon
from bbq_race.schemas import CouponOut, RedemptionOut


class VulnerableCouponRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, code: str) -> CouponOut | None:
        coupon = await self._session.scalar(select(Coupon).where(Coupon.code == code))
        return CouponOut.model_validate(coupon) if coupon is not None else None

    async def redeem(self, code: str) -> RedemptionOut | None:
        coupon = await self._session.scalar(select(Coupon).where(Coupon.code == code))
        if coupon is None or coupon.uses_left <= 0:
            return None

        # Celowe okno TOCTOU dla stabilnej demonstracji; opóźnienie nie jest
        # konieczne, by podatność istniała, tylko zwiększa szansę wyścigu.
        await asyncio.sleep(0.15)
        coupon.uses_left -= 1
        await self._session.commit()
        return RedemptionOut(
            code=coupon.code,
            discount_percent=coupon.discount_percent,
            uses_left=coupon.uses_left,
        )
