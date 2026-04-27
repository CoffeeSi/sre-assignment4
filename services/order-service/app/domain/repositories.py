from abc import ABC, abstractmethod

from app.domain.models import Order


class IOrderRepository(ABC):
    @abstractmethod
    async def get_by_id_for_user(self, order_id: int, user_id: int) -> Order | None: ...

    @abstractmethod
    async def get_all_for_user(self, user_id: int) -> list[Order]: ...

    @abstractmethod
    async def create(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
    ) -> Order: ...
