from fastapi import Depends, Request

from app.infrastructure.repositories import PostgresUserRepository
from app.application.use_cases import CreateUserUseCase, GetUserUseCase


def get_user_repository(request: Request) -> PostgresUserRepository:
    return PostgresUserRepository(pool=request.app.state.pool)


def get_create_user_use_case(
    repo: PostgresUserRepository = Depends(get_user_repository),
) -> CreateUserUseCase:
    return CreateUserUseCase(repository=repo)


def get_get_user_use_case(
    repo: PostgresUserRepository = Depends(get_user_repository),
) -> GetUserUseCase:
    return GetUserUseCase(repository=repo)
