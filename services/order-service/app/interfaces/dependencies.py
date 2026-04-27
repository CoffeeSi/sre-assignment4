from fastapi import Depends, Request

from app.infrastructure.repositories import PostgresOrderRepository
from app.application.use_cases import CreateOrderUseCase, GetOrderUseCase, GetAllOrdersUseCase


def get_order_repository(request: Request) -> PostgresOrderRepository:
    return PostgresOrderRepository(pool=request.app.state.pool)


def get_create_order_use_case(
    repo: PostgresOrderRepository = Depends(get_order_repository),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repository=repo)


def get_get_order_use_case(
    repo: PostgresOrderRepository = Depends(get_order_repository),
) -> GetOrderUseCase:
    return GetOrderUseCase(repository=repo)


def get_get_all_orders_use_case(
    repo: PostgresOrderRepository = Depends(get_order_repository),
) -> GetAllOrdersUseCase:
    return GetAllOrdersUseCase(repository=repo)
