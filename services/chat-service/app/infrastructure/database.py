import asyncio
import socket
import logging
from fastapi import FastAPI
from redis import asyncio as redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_redis(app: FastAPI, url: str) -> None:
    max_retries = 10
    retry_delay = 5

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_retries}: Connecting to Redis...")
            app.state.redis = redis.from_url(url, decode_responses=True)

            # Проверяем соединение
            await app.state.redis.ping()

            logger.info("Chat Service: Successfully connected to Redis.")
            return

        except (redis.ConnectionError, socket.gaierror, OSError) as e:
            logger.warning(f"Chat Service: Redis not ready (Attempt {attempt}): {e}")
            if attempt == max_retries:
                logger.error("Chat Service: Max retries reached for Redis.")
                raise e
            await asyncio.sleep(retry_delay)


async def close_redis(app: FastAPI) -> None:
    if hasattr(app.state, "redis"):
        await app.state.redis.close()
        logger.info("Chat Service: Redis connection closed.")
