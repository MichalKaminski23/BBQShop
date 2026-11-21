"""Wspólny interfejs operacji na kuponie."""

from typing import Protocol

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from bbq_db.models import Coupon
from bbq_race.schemas import CouponOut, RedemptionOut


async def reset_demo_coupon(session: AsyncSession) -> CouponOut | None:
    """Reset only the fixed GRILL10 demonstration coupon."""
    result = await session.execute(
        update(Coupon)
        .where(Coupon.code == "GRILL10")
        .values(uses_left=1)
        .returning(Coupon.discount_percent, Coupon.uses_left)
    )
    coupon = result.one_or_none()
    if coupon is None:
        await session.rollback()
        return None

    await session.commit()
    return CouponOut(
        code="GRILL10",
        discount_percent=coupon.discount_percent,
        uses_left=coupon.uses_left,
    )


class CouponRepository(Protocol):
    def __init__(self, session: AsyncSession) -> None: ...

    async def get(self, code: str) -> CouponOut | None: ...

    async def redeem(self, code: str) -> RedemptionOut | None: ...
