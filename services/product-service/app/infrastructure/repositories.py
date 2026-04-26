import asyncpg

from app.domain.models import Product
from app.domain.repositories import IProductRepository


class PostgresProductRepository(IProductRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_by_id(self, product_id: int) -> Product | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, price, created_at FROM products WHERE id = $1",
                product_id,
            )
        if row is None:
            return None
        return Product(id=row["id"], name=row["name"], price=row["price"], created_at=row["created_at"])

    async def create(self, name: str, price: float) -> Product:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO products(name, price) VALUES($1, $2) "
                "RETURNING id, name, price, created_at",
                name,
                price,
            )
        return Product(id=row["id"], name=row["name"], price=row["price"], created_at=row["created_at"])

    async def list_all(self) -> list[Product]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, name, price, created_at FROM products ORDER BY id"
            )
        return [
            Product(id=r["id"], name=r["name"], price=r["price"], created_at=r["created_at"])
            for r in rows
        ]
