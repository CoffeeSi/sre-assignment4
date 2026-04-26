import asyncpg
from fastapi import FastAPI


async def create_pool(app: FastAPI, dsn: str) -> None:
    app.state.pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                total_price NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )


async def close_pool(app: FastAPI) -> None:
    await app.state.pool.close()
