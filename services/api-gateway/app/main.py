import logging
import os
import sys
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pythonjsonlogger import jsonlogger

UPSTREAMS: dict[str, str] = {
    "/register": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
    "/login": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
    "/auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
    "/users": os.getenv("USER_SERVICE_URL", "http://user-service:8001"),
    "/products": os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002"),
    "/orders": os.getenv("ORDER_SERVICE_URL", "http://order-service:8003"),
    "/rooms": os.getenv("CHAT_SERVICE_URL", "http://chat-service:8005"),
}

_ROUTE_TABLE = sorted(UPSTREAMS.items(), key=lambda x: len(x[0]), reverse=True)


def _resolve_upstream(path: str) -> str | None:
    """Return the upstream base URL for the given request path, or None."""
    for prefix, upstream in _ROUTE_TABLE:
        if path == prefix or path.startswith(prefix + "/"):
            return upstream
    return None


_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
    }
)


_UPSTREAM_TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "30"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=_UPSTREAM_TIMEOUT)
    yield
    await app.state.http_client.aclose()


def _setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


_setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="api-gateway", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter(
    "api_gateway_requests_total",
    "Total HTTP requests handled by the API Gateway",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "api_gateway_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "api-gateway"})


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def proxy(request: Request, full_path: str) -> Response:
    path = "/" + full_path
    upstream = _resolve_upstream(path)
    if upstream is None:
        raise HTTPException(status_code=404, detail=f"No route for path: {path}")

    query = request.url.query
    target_url = upstream + path + (f"?{query}" if query else "")

    forward_headers = {
        k: v for k, v in request.headers.items() if k.lower() not in _HOP_BY_HOP
    }

    body = await request.body()

    logger.info(
        "proxying request",
        extra={"method": request.method, "path": path, "upstream": upstream},
    )

    with REQUEST_LATENCY.labels(method=request.method, path=path).time():
        try:
            upstream_response = await request.app.state.http_client.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                content=body,
            )
        except httpx.RequestError as exc:
            logger.error("upstream request failed", extra={"error": str(exc)})
            raise HTTPException(
                status_code=502, detail="Bad gateway: upstream service unavailable"
            )

    REQUEST_COUNT.labels(
        method=request.method,
        path=path,
        status_code=upstream_response.status_code,
    ).inc()

    response_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )
