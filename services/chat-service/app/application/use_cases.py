from app.domain.exceptions import UserNotFoundError
from app.domain.models import Message
from app.domain.repositories import IMessageRepository
from app.infrastructure.http_clients import verify_user_exists
from app.application.schemas import (
    MessageCreate,
    MessageOut,
    RoomMessagesResponse,
    SendMessageResponse,
)


class SendMessageUseCase:
    def __init__(self, repository: IMessageRepository) -> None:
        self._repository = repository

    async def execute(self, room: str, data: MessageCreate) -> SendMessageResponse:
        await verify_user_exists(data.user_id)
        message = Message(user_id=data.user_id, text=data.text)
        await self._repository.save(room=room, message=message)
        return SendMessageResponse(
            room=room, message=MessageOut(user_id=message.user_id, text=message.text)
        )


class GetMessagesUseCase:
    def __init__(self, repository: IMessageRepository) -> None:
        self._repository = repository

    async def execute(self, room: str, limit: int) -> RoomMessagesResponse:
        messages = await self._repository.get_recent(room=room, limit=limit)
        return RoomMessagesResponse(
            room=room,
            messages=[MessageOut(user_id=m.user_id, text=m.text) for m in messages],
        )
