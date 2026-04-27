import os
import sys
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from pythonjsonlogger import jsonlogger

from app.infrastructure.database import close_redis, create_redis
from app.interfaces.router import router

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_redis(app, REDIS_URL)
    yield
    await close_redis(app)


# Basic JSON logging setup
def _setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    # avoid duplicate handlers
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


_setup_logging()


app = FastAPI(title="chat-service", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus metric: total HTTP requests handled by this service
REQUEST_COUNT = Counter("chat_service_requests_total", "Total HTTP requests")


@app.middleware("http")
async def _metrics_middleware(request: Request, call_next):
    try:
        REQUEST_COUNT.inc()
    except Exception:
        pass
    response = await call_next(request)
    return response


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


app.include_router(router)
