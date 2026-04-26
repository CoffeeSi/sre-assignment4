import os

import httpx

from app.domain.exceptions import UserNotFoundError

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")


async def verify_user_exists(user_id: int) -> None:
    async with httpx.AsyncClient(timeout=3.0) as client:
        resp = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
    if resp.status_code != 200:
        raise UserNotFoundError(f"User {user_id} not found in user-service")
