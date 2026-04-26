from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas import UserCreate, UserResponse
from app.application.use_cases import CreateUserUseCase, GetUserUseCase
from app.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.interfaces.dependencies import get_create_user_use_case, get_get_user_use_case

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "user-service", "status": "ok"}


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserResponse:
    try:
        return await use_case.execute(payload)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already exists")


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
) -> UserResponse:
    try:
        return await use_case.execute(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
