import asyncpg

from app.domain.models import Order
from app.domain.repositories import IOrderRepository


class PostgresOrderRepository(IOrderRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_by_id_for_user(self, order_id: int, user_id: int) -> Order | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, user_id, product_id, quantity, total_price, created_at "
                "FROM orders WHERE id = $1 AND user_id = $2",
                order_id,
                user_id,
            )
        if row is None:
            return None
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            total_price=row["total_price"],
            created_at=row["created_at"],
        )

    async def get_all_for_user(self, user_id: int) -> list[Order]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, user_id, product_id, quantity, total_price, created_at "
                "FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
                user_id,
            )
        return [
            Order(
                id=row["id"],
                user_id=row["user_id"],
                product_id=row["product_id"],
                quantity=row["quantity"],
                total_price=row["total_price"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def create(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
    ) -> Order:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO orders(user_id, product_id, quantity, total_price) "
                "VALUES($1, $2, $3, $4) "
                "RETURNING id, user_id, product_id, quantity, total_price, created_at",
                user_id,
                product_id,
                quantity,
                total_price,
            )
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            total_price=row["total_price"],
            created_at=row["created_at"],
        )
