from datetime import datetime

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str


class RegisterResponse(BaseModel):
    id: int
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class VerifyResponse(BaseModel):
    user_id: int
    email: str
