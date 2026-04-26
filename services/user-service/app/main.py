import os

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/app_db"
)
ASYNC_PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

app = FastAPI(title="user-service", version="1.0.0")


class UserCreate(BaseModel):
    name: str
    email: EmailStr


@app.on_event("startup")
async def startup() -> None:
    app.state.pool = await asyncpg.create_pool(ASYNC_PG_DSN, min_size=1, max_size=5)
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


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.pool.close()


@app.get("/health")
async def health() -> dict:
    return {"service": "user-service", "status": "ok"}


@app.post("/users")
async def create_user(payload: UserCreate) -> dict:
    async with app.state.pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "INSERT INTO users(name, email) VALUES($1, $2) RETURNING id, name, email",
                payload.name,
                payload.email,
            )
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=409, detail="Email already exists")

    return dict(row)


@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, email, created_at FROM users WHERE id = $1",
            user_id,
        )

    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(row)
