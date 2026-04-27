from app.domain.models import Message
from app.domain.repositories import IMessageRepository
from app.application.schemas import (
    MessageCreate,
    MessageOut,
    RoomMessagesResponse,
    SendMessageResponse,
)


class SendMessageUseCase:
    def __init__(self, repository: IMessageRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        room: str,
        data: MessageCreate,
        user_id: int,
        user_name: str,
    ) -> SendMessageResponse:
        message = Message(user_id=user_id, user_name=user_name, text=data.text)
        await self._repository.save(room=room, message=message)
        return SendMessageResponse(
            room=room,
            message=MessageOut(user_name=message.user_name, text=message.text),
        )


class GetMessagesUseCase:
    def __init__(self, repository: IMessageRepository) -> None:
        self._repository = repository

    async def execute(self, room: str, limit: int) -> RoomMessagesResponse:
        messages = await self._repository.get_recent(room=room, limit=limit)
        return RoomMessagesResponse(
            room=room,
            messages=[MessageOut(user_name=m.user_name, text=m.text) for m in messages],
        )
