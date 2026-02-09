from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentops.api.middleware.cost_breaker import CostBreakerMiddleware
from agentops.api.middleware.rate_limit import RateLimitMiddleware
from agentops.api.middleware.request_id import RequestIDMiddleware
from agentops.api.routers import evaluations, guardrails, health, metrics, runs, ws
from agentops.config import settings
from agentops.observability.logger import get_logger
from agentops.observability.tracer import setup_tracing

logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", environment=settings.api_env)
    setup_tracing()
    yield
    logger.info("app_stopping")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentOps API",
        description="Production-grade multi-agent system with full observability",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # Middleware (order matters — outermost first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CostBreakerMiddleware)

    # Routers
    prefix = "/api/v1"
    app.include_router(health.router, prefix=prefix)
    app.include_router(runs.router, prefix=prefix)
    app.include_router(metrics.router, prefix=prefix)
    app.include_router(evaluations.router, prefix=prefix)
    app.include_router(guardrails.router, prefix=prefix)
    app.include_router(ws.router, prefix=prefix)

    return app
