import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))


class PasswordHasher:
    def hash(self, plain: str) -> str:
        return _pwd_context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)


class TokenService:
    def generate(self, user_id: int, email: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
        payload = {"sub": str(user_id), "email": email, "exp": expire}
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def decode(self, token: str) -> dict:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
