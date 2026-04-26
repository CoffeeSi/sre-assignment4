from abc import ABC, abstractmethod

from app.domain.models import Product


class IProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    async def create(self, name: str, price: float) -> Product: ...

    @abstractmethod
    async def list_all(self) -> list[Product]: ...
