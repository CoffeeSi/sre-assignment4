from app.domain.exceptions import ProductNotFoundError
from app.domain.repositories import IProductRepository
from app.application.schemas import ProductCreate, ProductResponse


class CreateProductUseCase:
    def __init__(self, repository: IProductRepository) -> None:
        self._repository = repository

    async def execute(self, data: ProductCreate) -> ProductResponse:
        product = await self._repository.create(name=data.name, price=data.price)
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            created_at=product.created_at,
        )


class GetProductUseCase:
    def __init__(self, repository: IProductRepository) -> None:
        self._repository = repository

    async def execute(self, product_id: int) -> ProductResponse:
        product = await self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            created_at=product.created_at,
        )


class ListProductsUseCase:
    def __init__(self, repository: IProductRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[ProductResponse]:
        products = await self._repository.list_all()
        return [
            ProductResponse(
                id=p.id, name=p.name, price=p.price, created_at=p.created_at
            )
            for p in products
        ]
