import asyncpg
from fastapi import FastAPI


async def create_pool(app: FastAPI, dsn: str) -> None:
    app.state.pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )


async def close_pool(app: FastAPI) -> None:
    await app.state.pool.close()
