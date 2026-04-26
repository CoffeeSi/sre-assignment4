from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Order:
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: Decimal
    created_at: datetime
