from abc import ABC, abstractmethod

from app.domain.models import AuthUser


class IAuthUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> AuthUser | None: ...

    @abstractmethod
    async def create(self, email: str, password_hash: str) -> AuthUser: ...
