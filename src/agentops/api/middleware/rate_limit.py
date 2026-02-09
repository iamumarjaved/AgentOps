import time

import redis.asyncio as aioredis
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from agentops.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiter backed by Redis."""

    def __init__(self, app, redis_url: str | None = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.redis_url
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and metrics
        if request.url.path in ("/api/v1/health", "/api/v1/health/ready", "/api/v1/metrics/prometheus"):
            return await call_next(request)

        # Use API key or IP as identifier
        api_key = request.headers.get("X-API-Key", "")
        identifier = api_key[:10] if api_key else request.client.host if request.client else "unknown"

        try:
            redis = await self._get_redis()
            key = f"ratelimit:{identifier}"
            now = time.time()
            window = 60  # 1 minute window

            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = await pipe.execute()

            request_count = results[2]
            limit = settings.rate_limit_requests_per_minute

            if request_count > limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Limit: {limit}/minute",
                )
        except HTTPException:
            raise
        except Exception:
            # If Redis is unavailable, allow the request
            pass

        response = await call_next(request)
        return response
