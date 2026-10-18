"""Server-Sent Events (SSE) endpoint for real-time dashboard updates."""
import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.services.monitoring_service import add_sse_subscriber, remove_sse_subscriber

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/stream")
async def event_stream() -> EventSourceResponse:
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    def _callback(event: dict) -> None:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # drop if consumer is slow

    add_sse_subscriber(_callback)

    async def generator() -> AsyncGenerator[dict, None]:
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {"data": json.dumps(event)}
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield {"data": json.dumps({"type": "heartbeat"})}
        except asyncio.CancelledError:
            pass
        finally:
            remove_sse_subscriber(_callback)

    return EventSourceResponse(generator())
