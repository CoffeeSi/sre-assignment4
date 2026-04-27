import json

from redis.asyncio import Redis

from app.domain.models import Message
from app.domain.repositories import IMessageRepository


class RedisMessageRepository(IMessageRepository):
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def save(self, room: str, message: Message) -> None:
        key = f"room:{room}:messages"
        await self._redis.rpush(
            key,
            json.dumps(
                {
                    "user_id": message.user_id,
                    "user_name": message.user_name,
                    "text": message.text,
                }
            ),
        )

    async def get_recent(self, room: str, limit: int) -> list[Message]:
        limit = max(1, min(limit, 200))
        key = f"room:{room}:messages"
        items = await self._redis.lrange(key, -limit, -1)
        messages: list[Message] = []
        for item in items:
            parsed = json.loads(item)
            messages.append(
                Message(
                    user_id=parsed["user_id"],
                    user_name=parsed.get("user_name", "Anonymous"),
                    text=parsed["text"],
                )
            )
        return messages
