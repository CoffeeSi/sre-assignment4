import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter("user_service_requests_total", "Total HTTP requests")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    try:
        REQUEST_COUNT.inc()
    except Exception:
        pass
    return await call_next(request)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(router)
