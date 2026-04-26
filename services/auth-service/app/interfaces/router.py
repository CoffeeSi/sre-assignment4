from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    VerifyResponse,
)
from app.application.use_cases import LoginUseCase, RegisterUseCase, VerifyTokenUseCase
from app.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from app.interfaces.dependencies import (
    get_login_use_case,
    get_register_use_case,
    get_verify_token_use_case,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "auth-service", "status": "ok"}


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    use_case: RegisterUseCase = Depends(get_register_use_case),
) -> RegisterResponse:
    try:
        return await use_case.execute(payload)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User already exists")


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> LoginResponse:
    try:
        return await use_case.execute(payload)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/auth/verify", response_model=VerifyResponse)
async def verify_token(
    token: str,
    use_case: VerifyTokenUseCase = Depends(get_verify_token_use_case),
) -> VerifyResponse:
    try:
        return use_case.execute(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
