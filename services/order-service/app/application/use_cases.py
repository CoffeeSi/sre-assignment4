from app.domain.exceptions import OrderNotFoundError, ProductNotFoundError, UserNotFoundError
from app.domain.repositories import IOrderRepository
from app.infrastructure.http_clients import get_product_price, verify_user_exists
from app.application.schemas import OrderCreate, OrderResponse


class CreateOrderUseCase:
    def __init__(self, repository: IOrderRepository) -> None:
        self._repository = repository

    async def execute(self, data: OrderCreate) -> OrderResponse:
        await verify_user_exists(data.user_id)
        product_price = await get_product_price(data.product_id)
        total_price = product_price * data.quantity
        order = await self._repository.create(
            user_id=data.user_id,
            product_id=data.product_id,
            quantity=data.quantity,
            total_price=total_price,
        )
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            total_price=order.total_price,
            created_at=order.created_at,
        )


class GetOrderUseCase:
    def __init__(self, repository: IOrderRepository) -> None:
        self._repository = repository

    async def execute(self, order_id: int) -> OrderResponse:
        order = await self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            total_price=order.total_price,
            created_at=order.created_at,
        )
