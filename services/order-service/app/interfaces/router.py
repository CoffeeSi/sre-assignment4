from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas import OrderCreate, OrderResponse, OrdersListResponse
from app.application.use_cases import CreateOrderUseCase, GetOrderUseCase, GetAllOrdersUseCase
from app.domain.exceptions import (
    OrderNotFoundError,
    ProductNotFoundError,
    UserNotFoundError,
)
from app.interfaces.dependencies import get_create_order_use_case, get_get_order_use_case, get_get_all_orders_use_case

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "order-service", "status": "ok"}


@router.get("/orders", response_model=OrdersListResponse)
async def get_all_orders(
    use_case: GetAllOrdersUseCase = Depends(get_get_all_orders_use_case),
) -> OrdersListResponse:
    return await use_case.execute()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    payload: OrderCreate,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> OrderResponse:
    try:
        return await use_case.execute(payload)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    use_case: GetOrderUseCase = Depends(get_get_order_use_case),
) -> OrderResponse:
    try:
        return await use_case.execute(order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
