import asyncio
import asyncpg
import socket
import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_pool(app: FastAPI, dsn: str) -> None:
    max_retries = 10
    retry_delay = 5

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Attempt {attempt}/{max_retries}: Auth Service is connecting to DB..."
            )

            app.state.pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)

            async with app.state.pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS auth_users (
                        id SERIAL PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    """
                )
            logger.info("Auth Service: Successfully connected and table initialized.")
            return

        except (socket.gaierror, ConnectionRefusedError, OSError) as e:
            logger.warning(f"Auth Service: DB not ready (Attempt {attempt}): {e}")
            if attempt == max_retries:
                logger.error("Auth Service: Max retries reached. Connection failed.")
                raise e
            await asyncio.sleep(retry_delay)


async def close_pool(app: FastAPI) -> None:
    if hasattr(app.state, "pool"):
        await app.state.pool.close()
        logger.info("Auth Service: DB pool closed.")
