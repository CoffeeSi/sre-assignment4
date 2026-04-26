import os

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/app_db"
)
ASYNC_PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

app = FastAPI(title="auth-service", version="1.0.0")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@app.on_event("startup")
async def startup() -> None:
    app.state.pool = await asyncpg.create_pool(ASYNC_PG_DSN, min_size=1, max_size=5)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.pool.close()


@app.get("/health")
async def health() -> dict:
    return {"service": "auth-service", "status": "ok"}


@app.post("/register")
async def register(payload: RegisterRequest) -> dict:
    async with app.state.pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "INSERT INTO auth_users(email, password) VALUES($1, $2) RETURNING id, email",
                payload.email,
                payload.password,
            )
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=409, detail="User already exists")

    return {"id": row["id"], "email": row["email"]}


@app.post("/login")
async def login(payload: LoginRequest) -> dict:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email FROM auth_users WHERE email = $1 AND password = $2",
            payload.email,
            payload.password,
        )

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user": {"id": row["id"], "email": row["email"]},
    }
