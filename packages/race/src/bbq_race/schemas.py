"""Schematy API modułu Race."""

from pydantic import BaseModel, ConfigDict, Field


class RedeemRequest(BaseModel):
    code: str = Field(min_length=1, max_length=32)


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    discount_percent: int
    uses_left: int


class RedemptionOut(BaseModel):
    code: str
    discount_percent: int
    uses_left: int
    message: str = "Kupon został wykorzystany."
