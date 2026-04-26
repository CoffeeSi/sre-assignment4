from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas import (
    MessageCreate,
    RoomMessagesResponse,
    SendMessageResponse,
)
from app.application.use_cases import GetMessagesUseCase, SendMessageUseCase
from app.domain.exceptions import UserNotFoundError
from app.interfaces.dependencies import get_get_messages_use_case, get_send_message_use_case

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "chat-service", "status": "ok"}


@router.post("/rooms/{room}/messages", response_model=SendMessageResponse, status_code=201)
async def send_message(
    room: str,
    payload: MessageCreate,
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
) -> SendMessageResponse:
    try:
        return await use_case.execute(room=room, data=payload)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found in user-service")


@router.get("/rooms/{room}/messages", response_model=RoomMessagesResponse)
async def get_messages(
    room: str,
    limit: int = 50,
    use_case: GetMessagesUseCase = Depends(get_get_messages_use_case),
) -> RoomMessagesResponse:
    return await use_case.execute(room=room, limit=limit)
