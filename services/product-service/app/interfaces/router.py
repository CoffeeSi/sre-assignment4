from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas import ProductCreate, ProductResponse
from app.application.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsUseCase,
)
from app.domain.exceptions import ProductNotFoundError
from app.interfaces.dependencies import (
    get_create_product_use_case,
    get_get_product_use_case,
    get_list_products_use_case,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "product-service", "status": "ok"}


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
) -> ProductResponse:
    return await use_case.execute(payload)


@router.get("/products", response_model=list[ProductResponse])
async def list_products(
    use_case: ListProductsUseCase = Depends(get_list_products_use_case),
) -> list[ProductResponse]:
    return await use_case.execute()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
) -> ProductResponse:
    try:
        return await use_case.execute(product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
