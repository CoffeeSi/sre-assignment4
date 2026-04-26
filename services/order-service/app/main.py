import os

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/app_db"
)
ASYNC_PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

app = FastAPI(title="order-service", version="1.0.0")


class OrderCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


@app.on_event("startup")
async def startup() -> None:
    app.state.pool = await asyncpg.create_pool(ASYNC_PG_DSN, min_size=1, max_size=5)
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


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.pool.close()


@app.get("/health")
async def health() -> dict:
    return {"service": "order-service", "status": "ok"}


@app.post("/orders")
async def create_order(payload: OrderCreate) -> dict:
    async with app.state.pool.acquire() as conn:
        user_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE id = $1", payload.user_id
        )
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")

        product_price = await conn.fetchval(
            "SELECT price FROM products WHERE id = $1", payload.product_id
        )
        if product_price is None:
            raise HTTPException(status_code=404, detail="Product not found")

        total_price = float(product_price) * payload.quantity
        row = await conn.fetchrow(
            """
            INSERT INTO orders(user_id, product_id, quantity, total_price)
            VALUES($1, $2, $3, $4)
            RETURNING id, user_id, product_id, quantity, total_price
            """,
            payload.user_id,
            payload.product_id,
            payload.quantity,
            total_price,
        )

    return dict(row)


@app.get("/orders/{order_id}")
async def get_order(order_id: int) -> dict:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, user_id, product_id, quantity, total_price, created_at FROM orders WHERE id = $1",
            order_id,
        )

    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return dict(row)
