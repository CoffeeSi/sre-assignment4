import json
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from redis import asyncio as redis


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")

app = FastAPI(title="chat-service", version="1.0.0")


class MessageCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    text: str = Field(..., min_length=1, max_length=500)


@app.on_event("startup")
async def startup() -> None:
    app.state.redis = redis.from_url(REDIS_URL, decode_responses=True)
    await app.state.redis.ping()


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.redis.close()


@app.get("/health")
async def health() -> dict:
    return {"service": "chat-service", "status": "ok"}


@app.post("/rooms/{room}/messages")
async def send_message(room: str, payload: MessageCreate) -> dict:
    async with httpx.AsyncClient(timeout=3.0) as client:
        user_resp = await client.get(f"{USER_SERVICE_URL}/users/{payload.user_id}")

    if user_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="User not found in user-service")

    message = {"user_id": payload.user_id, "text": payload.text}
    key = f"room:{room}:messages"
    await app.state.redis.rpush(key, json.dumps(message))
    return {"room": room, "message": message}


@app.get("/rooms/{room}/messages")
async def get_messages(room: str, limit: int = 50) -> dict:
    key = f"room:{room}:messages"
    limit = max(1, min(limit, 200))
    items = await app.state.redis.lrange(key, -limit, -1)
    messages = [json.loads(item) for item in items]
    return {"room": room, "messages": messages}
