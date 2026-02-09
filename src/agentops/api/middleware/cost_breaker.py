from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from agentops.config import settings
from agentops.observability.logger import get_logger
from agentops.observability.metrics import cost_usd_total

logger = get_logger("middleware.cost_breaker")


class CostBreakerMiddleware(BaseHTTPMiddleware):
    """Circuit breaker that stops new runs if cost threshold is exceeded."""

    async def dispatch(self, request: Request, call_next):
        # Only check cost for run creation
        if request.method == "POST" and "/runs" in request.url.path:
            total_cost = 0.0
            # Sum up all cost counters
            for metric in cost_usd_total.collect():
                for sample in metric.samples:
                    if sample.name == "agentops_cost_usd_total_total":
                        total_cost += sample.value

            daily_limit = settings.max_cost_per_run_usd * 100  # rough daily budget
            if total_cost > daily_limit:
                logger.error("cost_breaker_triggered", total_cost=total_cost, limit=daily_limit)
                raise HTTPException(
                    status_code=503,
                    detail=f"Cost circuit breaker triggered. Total cost: ${total_cost:.2f}",
                )

        return await call_next(request)
