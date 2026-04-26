from abc import ABC, abstractmethod

from app.domain.models import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def create(self, name: str, email: str) -> User: ...
