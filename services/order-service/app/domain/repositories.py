from abc import ABC, abstractmethod

from app.domain.models import Order


class IOrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None: ...

    @abstractmethod
    async def get_all(self) -> list[Order]: ...

    @abstractmethod
    async def create(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
    ) -> Order: ...
