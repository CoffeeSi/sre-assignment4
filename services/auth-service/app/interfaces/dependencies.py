from fastapi import Depends, Request

from app.domain.services import PasswordHasher, TokenService
from app.infrastructure.repositories import PostgresAuthUserRepository
from app.application.use_cases import LoginUseCase, RegisterUseCase, VerifyTokenUseCase

_password_hasher = PasswordHasher()
_token_service = TokenService()


def get_auth_repository(request: Request) -> PostgresAuthUserRepository:
    return PostgresAuthUserRepository(pool=request.app.state.pool)


def get_register_use_case(
    repo: PostgresAuthUserRepository = Depends(get_auth_repository),
) -> RegisterUseCase:
    return RegisterUseCase(repository=repo, hasher=_password_hasher)


def get_login_use_case(
    repo: PostgresAuthUserRepository = Depends(get_auth_repository),
) -> LoginUseCase:
    return LoginUseCase(
        repository=repo,
        hasher=_password_hasher,
        token_service=_token_service,
    )


def get_verify_token_use_case() -> VerifyTokenUseCase:
    return VerifyTokenUseCase(token_service=_token_service)
