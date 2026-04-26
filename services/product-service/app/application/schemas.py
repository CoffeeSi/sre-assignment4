from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    price: float = Field(..., gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    created_at: datetime
