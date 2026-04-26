import asyncpg

from app.domain.exceptions import UserAlreadyExistsError
from app.domain.models import User
from app.domain.repositories import IUserRepository


class PostgresUserRepository(IUserRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_by_id(self, user_id: int) -> User | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, email, created_at FROM users WHERE id = $1", user_id
            )
        if row is None:
            return None
        return User(id=row["id"], name=row["name"], email=row["email"], created_at=row["created_at"])

    async def get_by_email(self, email: str) -> User | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, email, created_at FROM users WHERE email = $1", email
            )
        if row is None:
            return None
        return User(id=row["id"], name=row["name"], email=row["email"], created_at=row["created_at"])

    async def create(self, name: str, email: str) -> User:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "INSERT INTO users(name, email) VALUES($1, $2) "
                    "RETURNING id, name, email, created_at",
                    name,
                    email,
                )
        except asyncpg.UniqueViolationError as exc:
            raise UserAlreadyExistsError(f"Email {email} already exists") from exc
        return User(id=row["id"], name=row["name"], email=row["email"], created_at=row["created_at"])
