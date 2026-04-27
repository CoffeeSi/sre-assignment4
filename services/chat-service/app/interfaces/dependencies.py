import os
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.repositories import RedisMessageRepository
from app.application.use_cases import GetMessagesUseCase, SendMessageUseCase

_bearer_scheme = HTTPBearer(auto_error=False)
_jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
_jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")


@dataclass
class CurrentUser:
    user_id: int
    user_name: str


def _build_display_name(email: str | None, user_id: int) -> str:
    if not email:
        return "Anonymous"
    return email.strip() or "Anonymous"


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _jwt_secret_key,
            algorithms=[_jwt_algorithm],
        )
        user_id = int(payload["sub"])
        user_name = _build_display_name(payload.get("email"), user_id)
        return CurrentUser(user_id=user_id, user_name=user_name)
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_message_repository(request: Request) -> RedisMessageRepository:
    return RedisMessageRepository(redis_client=request.app.state.redis)


def get_send_message_use_case(
    repo: RedisMessageRepository = Depends(get_message_repository),
) -> SendMessageUseCase:
    return SendMessageUseCase(repository=repo)


def get_get_messages_use_case(
    repo: RedisMessageRepository = Depends(get_message_repository),
) -> GetMessagesUseCase:
    return GetMessagesUseCase(repository=repo)
