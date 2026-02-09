import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.api.middleware.auth import AuthDep
from agentops.api.schemas.requests import RunCreate
from agentops.api.schemas.responses import (
    AgentStepResponse,
    RunCreatedResponse,
    RunDetailResponse,
    RunResponse,
)
from agentops.db.engine import get_session
from agentops.db.repositories.runs import AgentStepRepository, RunRepository
from agentops.workers.tasks import run_pipeline

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunCreatedResponse, status_code=202)
async def create_run(
    body: RunCreate,
    auth: AuthDep,
    session: AsyncSession = Depends(get_session),
):
    """Trigger a new agent pipeline run."""
    repo = RunRepository(session)
    run = await repo.create(topic=body.topic, config=body.config)
    await session.commit()

    # Dispatch to Celery worker
    run_pipeline.delay(str(run.id), body.topic, body.config)

    return RunCreatedResponse(
        id=run.id,
        status="pending",
        message="Pipeline run queued successfully",
    )


@router.get("", response_model=list[RunResponse])
async def list_runs(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """List pipeline runs with optional status filter."""
    repo = RunRepository(session)
    runs = await repo.list_runs(status=status, limit=limit, offset=offset)
    return [RunResponse.model_validate(r) for r in runs]


@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run(
    run_id: uuid.UUID,
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get detailed information about a specific run."""
    repo = RunRepository(session)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    steps = [AgentStepResponse.model_validate(s) for s in run.steps]
    response = RunDetailResponse.model_validate(run)
    response.steps = steps
    return response


@router.get("/{run_id}/steps", response_model=list[AgentStepResponse])
async def get_run_steps(
    run_id: uuid.UUID,
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all agent steps for a specific run."""
    repo = AgentStepRepository(session)
    steps = await repo.get_steps_for_run(run_id)
    return [AgentStepResponse.model_validate(s) for s in steps]
