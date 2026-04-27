import os

import httpx

from app.domain.exceptions import ProductNotFoundError

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")

_http_client = httpx.AsyncClient(timeout=5.0)


async def get_product_price(product_id: int) -> float:
    resp = await _http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    if resp.status_code != 200:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return float(resp.json()["price"])
