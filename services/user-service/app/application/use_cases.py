from app.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.repositories import IUserRepository
from app.application.schemas import UserCreate, UserResponse


class CreateUserUseCase:
    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    async def execute(self, data: UserCreate) -> UserResponse:
        existing = await self._repository.get_by_email(data.email)
        if existing is not None:
            raise UserAlreadyExistsError(f"Email {data.email} already exists")
        user = await self._repository.create(name=data.name, email=data.email)
        return UserResponse(
            id=user.id, name=user.name, email=user.email, created_at=user.created_at
        )


class GetUserUseCase:
    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: int) -> UserResponse:
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return UserResponse(
            id=user.id, name=user.name, email=user.email, created_at=user.created_at
        )
