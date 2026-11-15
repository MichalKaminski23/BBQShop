"""Atomowy warunkowy UPDATE bez okna TOCTOU."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_db.models import Coupon
from bbq_race.schemas import CouponOut, RedemptionOut


class SecureCouponRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, code: str) -> CouponOut | None:
        coupon = await self._session.scalar(select(Coupon).where(Coupon.code == code))
        return CouponOut.model_validate(coupon) if coupon is not None else None

    async def redeem(self, code: str) -> RedemptionOut | None:
        result = await self._session.execute(
            update(Coupon)
            .where(Coupon.code == code, Coupon.uses_left > 0)
            .values(uses_left=Coupon.uses_left - 1)
            .returning(Coupon.discount_percent, Coupon.uses_left)
        )
        redeemed = result.one_or_none()
        if redeemed is None:
            await self._session.rollback()
            return None

        await self._session.commit()
        return RedemptionOut(
            code=code,
            discount_percent=redeemed.discount_percent,
            uses_left=redeemed.uses_left,
        )
