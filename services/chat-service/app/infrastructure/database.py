from fastapi import FastAPI
from redis import asyncio as redis


async def create_redis(app: FastAPI, url: str) -> None:
    app.state.redis = redis.from_url(url, decode_responses=True)
    await app.state.redis.ping()


async def close_redis(app: FastAPI) -> None:
    await app.state.redis.close()
