from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from bbq_db.base import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    discount_percent: Mapped[int]
    uses_left: Mapped[int]
