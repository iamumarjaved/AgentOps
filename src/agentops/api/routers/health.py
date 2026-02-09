import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.api.schemas.responses import HealthResponse, ReadyResponse
from agentops.config import settings
from agentops.db.engine import get_session

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", environment=settings.api_env)


@router.get("/health/ready", response_model=ReadyResponse)
async def readiness(session: AsyncSession = Depends(get_session)):
    db_status = "ok"
    redis_status = "ok"

    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
    except Exception:
        redis_status = "unavailable"

    status = "ready" if db_status == "ok" and redis_status == "ok" else "degraded"
    return ReadyResponse(status=status, database=db_status, redis=redis_status)
