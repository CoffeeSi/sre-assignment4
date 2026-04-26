import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database import close_pool, create_pool
from app.interfaces.router import router

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/app_db"
)
ASYNC_PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool(app, ASYNC_PG_DSN)
    yield
    await close_pool(app)


app = FastAPI(title="user-service", version="1.0.0", lifespan=lifespan)
app.include_router(router)
