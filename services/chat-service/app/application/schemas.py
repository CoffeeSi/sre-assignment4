from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class MessageOut(BaseModel):
    user_name: str
    text: str


class RoomMessagesResponse(BaseModel):
    room: str
    messages: list[MessageOut]


class SendMessageResponse(BaseModel):
    room: str
    message: MessageOut
