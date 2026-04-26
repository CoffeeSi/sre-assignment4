import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database import close_redis, create_redis
from app.interfaces.router import router

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_redis(app, REDIS_URL)
    yield
    await close_redis(app)


app = FastAPI(title="chat-service", version="1.0.0", lifespan=lifespan)
app.include_router(router)
