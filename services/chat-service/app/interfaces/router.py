from fastapi import APIRouter, Depends

from app.application.schemas import (
    MessageCreate,
    RoomMessagesResponse,
    SendMessageResponse,
)
from app.application.use_cases import GetMessagesUseCase, SendMessageUseCase
from app.interfaces.dependencies import (
    CurrentUser,
    get_current_user,
    get_get_messages_use_case,
    get_send_message_use_case,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "chat-service", "status": "ok"}


@router.post(
    "/rooms/{room}/messages", response_model=SendMessageResponse, status_code=201
)
async def send_message(
    room: str,
    payload: MessageCreate,
    current_user: CurrentUser = Depends(get_current_user),
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
) -> SendMessageResponse:
    return await use_case.execute(
        room=room,
        data=payload,
        user_id=current_user.user_id,
        user_name=current_user.user_name,
    )


@router.get("/rooms/{room}/messages", response_model=RoomMessagesResponse)
async def get_messages(
    room: str,
    limit: int = 50,
    use_case: GetMessagesUseCase = Depends(get_get_messages_use_case),
) -> RoomMessagesResponse:
    return await use_case.execute(room=room, limit=limit)
