from fastapi import APIRouter, Depends
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from agentops.api.middleware.auth import AuthDep
from agentops.api.schemas.responses import CostMetricsResponse, LatencyMetricsResponse, TokenMetricsResponse
from agentops.db.engine import get_session
from agentops.db.models import AgentStep, Run

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/prometheus")
async def prometheus_metrics():
    """Prometheus scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/cost", response_model=CostMetricsResponse)
async def cost_metrics(
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get cost breakdown metrics."""
    # Total cost
    total = await session.execute(select(func.sum(Run.total_cost_usd)))
    total_cost = total.scalar() or 0.0

    # Cost by agent
    by_agent = await session.execute(
        select(AgentStep.agent_name, func.sum(AgentStep.cost_usd))
        .group_by(AgentStep.agent_name)
    )
    cost_by_agent = {row[0]: round(float(row[1]), 6) for row in by_agent.all()}

    # Cost by day
    by_day = await session.execute(
        select(
            func.date_trunc("day", Run.created_at).label("day"),
            func.sum(Run.total_cost_usd),
        )
        .group_by("day")
        .order_by("day")
        .limit(30)
    )
    cost_by_day = [
        {"date": str(row[0]), "cost_usd": round(float(row[1]), 6)}
        for row in by_day.all()
    ]

    return CostMetricsResponse(
        total_cost_usd=round(float(total_cost), 6),
        cost_by_agent=cost_by_agent,
        cost_by_day=cost_by_day,
    )


@router.get("/tokens", response_model=TokenMetricsResponse)
async def token_metrics(
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get token usage metrics."""
    total = await session.execute(select(func.sum(Run.total_tokens)))
    total_tokens = total.scalar() or 0

    by_agent = await session.execute(
        select(
            AgentStep.agent_name,
            func.sum(AgentStep.input_tokens),
            func.sum(AgentStep.output_tokens),
        )
        .group_by(AgentStep.agent_name)
    )
    tokens_by_agent = {
        row[0]: {"input": int(row[1] or 0), "output": int(row[2] or 0)}
        for row in by_agent.all()
    }

    return TokenMetricsResponse(total_tokens=int(total_tokens), tokens_by_agent=tokens_by_agent)


@router.get("/latency", response_model=LatencyMetricsResponse)
async def latency_metrics(
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get latency metrics."""
    avg_result = await session.execute(
        select(func.avg(Run.total_latency_seconds)).where(Run.status == "completed")
    )
    avg_latency = avg_result.scalar() or 0.0

    # Approximate p95 using percentile_cont
    p95_result = await session.execute(
        select(
            func.percentile_cont(0.95).within_group(Run.total_latency_seconds)
        ).where(Run.status == "completed")
    )
    p95_latency = p95_result.scalar() or 0.0

    by_agent = await session.execute(
        select(AgentStep.agent_name, func.avg(AgentStep.latency_seconds))
        .group_by(AgentStep.agent_name)
    )
    latency_by_agent = {row[0]: round(float(row[1] or 0), 4) for row in by_agent.all()}

    return LatencyMetricsResponse(
        average_latency_seconds=round(float(avg_latency), 4),
        p95_latency_seconds=round(float(p95_latency), 4),
        latency_by_agent=latency_by_agent,
    )
