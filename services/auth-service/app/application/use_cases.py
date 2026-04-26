import jwt

from app.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from app.domain.repositories import IAuthUserRepository
from app.domain.services import PasswordHasher, TokenService
from app.application.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserOut,
    VerifyResponse,
)


class RegisterUseCase:
    def __init__(self, repository: IAuthUserRepository, hasher: PasswordHasher) -> None:
        self._repository = repository
        self._hasher = hasher

    async def execute(self, data: RegisterRequest) -> RegisterResponse:
        existing = await self._repository.get_by_email(data.email)
        if existing is not None:
            raise UserAlreadyExistsError(f"Email {data.email} already registered")
        password_hash = self._hasher.hash(data.password)
        user = await self._repository.create(email=data.email, password_hash=password_hash)
        return RegisterResponse(id=user.id, email=user.email)


class LoginUseCase:
    def __init__(
        self,
        repository: IAuthUserRepository,
        hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._repository = repository
        self._hasher = hasher
        self._token_service = token_service

    async def execute(self, data: LoginRequest) -> LoginResponse:
        user = await self._repository.get_by_email(data.email)
        if user is None or not self._hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        token = self._token_service.generate(user_id=user.id, email=user.email)
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserOut(id=user.id, email=user.email),
        )


class VerifyTokenUseCase:
    def __init__(self, token_service: TokenService) -> None:
        self._token_service = token_service

    def execute(self, token: str) -> VerifyResponse:
        try:
            payload = self._token_service.decode(token)
            return VerifyResponse(user_id=int(payload["sub"]), email=payload["email"])
        except (jwt.PyJWTError, KeyError, ValueError) as exc:
            raise InvalidTokenError("Token is invalid or expired") from exc
