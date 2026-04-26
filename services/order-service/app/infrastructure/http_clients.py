import os

import httpx

from app.domain.exceptions import ProductNotFoundError, UserNotFoundError

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")

_http_client = httpx.AsyncClient(timeout=5.0)


async def verify_user_exists(user_id: int) -> None:
    resp = await _http_client.get(f"{USER_SERVICE_URL}/users/{user_id}")
    if resp.status_code != 200:
        raise UserNotFoundError(f"User {user_id} not found")


async def get_product_price(product_id: int) -> float:
    resp = await _http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    if resp.status_code != 200:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return float(resp.json()["price"])
