from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: Decimal
    created_at: datetime


class OrdersListResponse(BaseModel):
    orders: list[OrderResponse]
