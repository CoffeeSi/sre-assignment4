from fastapi import Depends, Request

from app.infrastructure.repositories import PostgresProductRepository
from app.application.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsUseCase,
)


def get_product_repository(request: Request) -> PostgresProductRepository:
    return PostgresProductRepository(pool=request.app.state.pool)


def get_create_product_use_case(
    repo: PostgresProductRepository = Depends(get_product_repository),
) -> CreateProductUseCase:
    return CreateProductUseCase(repository=repo)


def get_get_product_use_case(
    repo: PostgresProductRepository = Depends(get_product_repository),
) -> GetProductUseCase:
    return GetProductUseCase(repository=repo)


def get_list_products_use_case(
    repo: PostgresProductRepository = Depends(get_product_repository),
) -> ListProductsUseCase:
    return ListProductsUseCase(repository=repo)
