from fastapi import Depends, Request

from app.infrastructure.repositories import RedisMessageRepository
from app.application.use_cases import GetMessagesUseCase, SendMessageUseCase


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
