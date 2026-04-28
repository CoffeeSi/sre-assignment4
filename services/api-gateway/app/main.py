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
    "/auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
    "/rooms": os.getenv("CHAT_SERVICE_URL", "http://chat-service:8005"),
    "/users": os.getenv("USER_SERVICE_URL", "http://user-service:8001"),
    "/products": os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002"),
    "/orders": os.getenv("ORDER_SERVICE_URL", "http://order-service:8003"),
}


_ROUTE_TABLE = sorted(UPSTREAMS.items(), key=lambda x: len(x[0]), reverse=True)


def _find_prefix(path: str) -> str | None:
    for prefix, _ in _ROUTE_TABLE:
        if path == prefix or path.startswith(prefix + "/"):
            return prefix
    return None


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
    allow_credentials=False,
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

    route_prefix = _find_prefix(path) or ""

    query = request.url.query

    # compute the path to send to upstream: strip the route prefix for service routes
    if route_prefix == "/" or route_prefix == "":
        upstream_path = path
    else:
        # remove the prefix from path; ensure it starts with '/'
        upstream_path = path[len(route_prefix) :]
        if not upstream_path:
            upstream_path = "/"

    target_url = upstream + upstream_path + (f"?{query}" if query else "")

    # Capture origin for CORS handling; don't forward Origin to upstream
    origin = request.headers.get("origin")
    forward_headers = {
        k: v for k, v in request.headers.items() if k.lower() not in _HOP_BY_HOP
    }
    forward_headers.pop("origin", None)

    # set Host header for upstream (some services rely on Host)
    try:
        # extract host:port from upstream URL
        host = upstream.split("//", 1)[1]
        forward_headers["host"] = host
    except Exception:
        pass

    # Fast-path preflight: respond with explicit CORS headers
    if request.method == "OPTIONS":
        ac_request_headers = request.headers.get("access-control-request-headers", "*")
        ac_allowed_methods = "GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD"
        cors_headers = {
            "Access-Control-Allow-Origin": origin or "*",
            "Access-Control-Allow-Methods": ac_allowed_methods,
            "Access-Control-Allow-Headers": ac_request_headers,
            "Access-Control-Max-Age": "3600",
        }
        return Response(status_code=200, headers=cors_headers)

    body = await request.body()

    logger.info(
        "proxying request",
        extra={
            "method": request.method,
            "path": path,
            "route_prefix": route_prefix,
            "upstream": upstream,
            "upstream_path": upstream_path,
        },
    )

    with REQUEST_LATENCY.labels(method=request.method, path=route_prefix).time():
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
        path=route_prefix,
        status_code=str(upstream_response.status_code),
    ).inc()

    response_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }

    # Ensure CORS Allow-Origin header on proxied responses
    if origin:
        response_headers.setdefault("Access-Control-Allow-Origin", origin)

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )
