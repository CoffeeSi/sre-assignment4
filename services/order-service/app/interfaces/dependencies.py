import os

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.repositories import PostgresOrderRepository
from app.application.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    GetAllOrdersUseCase,
)

_bearer_scheme = HTTPBearer(auto_error=False)
_jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
_jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> int:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _jwt_secret_key,
            algorithms=[_jwt_algorithm],
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")


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
