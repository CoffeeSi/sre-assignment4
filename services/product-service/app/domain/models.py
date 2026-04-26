from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Product:
    id: int
    name: str
    price: Decimal
    created_at: datetime
