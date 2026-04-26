from abc import ABC, abstractmethod

from app.domain.models import Message


class IMessageRepository(ABC):
    @abstractmethod
    async def save(self, room: str, message: Message) -> None: ...

    @abstractmethod
    async def get_recent(self, room: str, limit: int) -> list[Message]: ...
