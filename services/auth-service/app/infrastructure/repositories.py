import asyncpg

from app.domain.exceptions import UserAlreadyExistsError
from app.domain.models import AuthUser
from app.domain.repositories import IAuthUserRepository


class PostgresAuthUserRepository(IAuthUserRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_by_email(self, email: str) -> AuthUser | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, password, created_at FROM auth_users WHERE email = $1",
                email,
            )
        if row is None:
            return None
        return AuthUser(
            id=row["id"],
            email=row["email"],
            password_hash=row["password"],
            created_at=row["created_at"],
        )

    async def create(self, email: str, password_hash: str) -> AuthUser:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "INSERT INTO auth_users(email, password) VALUES($1, $2) "
                    "RETURNING id, email, password, created_at",
                    email,
                    password_hash,
                )
        except asyncpg.UniqueViolationError as exc:
            raise UserAlreadyExistsError(f"Email {email} already registered") from exc
        return AuthUser(
            id=row["id"],
            email=row["email"],
            password_hash=row["password"],
            created_at=row["created_at"],
        )
