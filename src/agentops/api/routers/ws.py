import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentops.config import settings
from agentops.observability.logger import get_logger

logger = get_logger("ws")
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{run_id}")
async def websocket_run_stream(websocket: WebSocket, run_id: str):
    """Stream real-time agent execution events via WebSocket."""
    await websocket.accept()

    try:
        redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"agentops:run:{run_id}")

        logger.info("websocket_connected", run_id=run_id)

        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

                # Close on completion
                if data.get("type") in ("run_completed", "run_failed"):
                    break

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", run_id=run_id)
    except Exception as e:
        logger.error("websocket_error", run_id=run_id, error=str(e))
    finally:
        try:
            await pubsub.unsubscribe(f"agentops:run:{run_id}")
            await redis.aclose()
        except Exception:
            pass
