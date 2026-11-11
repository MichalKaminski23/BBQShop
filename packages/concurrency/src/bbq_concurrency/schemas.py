"""Schematy żądań i odpowiedzi modułu współbieżności."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    created_at: datetime
    items: list[OrderItemOut]


class CreateOrderResult(BaseModel):
    order: OrderOut
    created: bool
