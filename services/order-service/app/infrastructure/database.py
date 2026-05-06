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
            logger.info(
                f"Attempt {attempt}/{max_retries}: Order Service is connecting to DB..."
            )

            app.state.pool = await asyncpg.create_pool(
                dsn,
                min_size=pool_min_size,
                max_size=pool_max_size,
            )

            async with app.state.pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        product_id INT NOT NULL,
                        quantity INT NOT NULL,
                        total_price NUMERIC(10, 2) NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    """
                )
                await conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_orders_user_id_created_at
                    ON orders (user_id, created_at DESC);
                    """
                )
                await conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_orders_product_id
                    ON orders (product_id);
                    """
                )
            logger.info("Order Service: Successfully connected and table initialized.")
            return

        except (socket.gaierror, ConnectionRefusedError, OSError) as e:
            logger.warning(
                f"Order Service: DB connection failed (Attempt {attempt}): {e}"
            )
            if attempt == max_retries:
                logger.error("Order Service: Max retries reached. Shutdown.")
                raise e
            await asyncio.sleep(retry_delay)


async def close_pool(app: FastAPI) -> None:
    if hasattr(app.state, "pool"):
        await app.state.pool.close()
        logger.info("Order Service: DB pool closed.")
