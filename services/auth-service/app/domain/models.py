from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthUser:
    id: int
    email: str
    password_hash: str
    created_at: datetime
