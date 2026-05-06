import asyncio
import asyncpg
import socket
import logging
import os
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_pool(app: FastAPI, dsn: str) -> None:
    max_retries = 10
    retry_delay = 5
    pool_min_size = int(os.getenv("DB_POOL_MIN_SIZE", "1"))
    pool_max_size = int(os.getenv("DB_POOL_MAX_SIZE", "20"))

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_retries}: Connecting to database...")

            app.state.pool = await asyncpg.create_pool(
                dsn,
                min_size=pool_min_size,
                max_size=pool_max_size,
            )

            async with app.state.pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    """
                )
            logger.info(
                "Successfully connected to the database and initialized tables."
            )
            return

        except (socket.gaierror, ConnectionRefusedError, OSError) as e:
            logger.warning(f"Database not ready yet (Attempt {attempt}): {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Could not connect to database.")
                raise e
            await asyncio.sleep(retry_delay)


async def close_pool(app: FastAPI) -> None:
    if hasattr(app.state, "pool"):
        await app.state.pool.close()
        logger.info("Database pool closed.")
