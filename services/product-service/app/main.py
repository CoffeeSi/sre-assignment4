import os

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/app_db"
)
ASYNC_PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

app = FastAPI(title="product-service", version="1.0.0")


class ProductCreate(BaseModel):
    name: str
    price: float = Field(..., gt=0)


@app.on_event("startup")
async def startup() -> None:
    app.state.pool = await asyncpg.create_pool(ASYNC_PG_DSN, min_size=1, max_size=5)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.pool.close()


@app.get("/health")
async def health() -> dict:
    return {"service": "product-service", "status": "ok"}


@app.post("/products")
async def create_product(payload: ProductCreate) -> dict:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO products(name, price) VALUES($1, $2) RETURNING id, name, price",
            payload.name,
            payload.price,
        )
    return dict(row)


@app.get("/products/{product_id}")
async def get_product(product_id: int) -> dict:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, price, created_at FROM products WHERE id = $1",
            product_id,
        )

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return dict(row)


@app.get("/products")
async def list_products() -> list[dict]:
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, price FROM products ORDER BY id")

    return [dict(r) for r in rows]
