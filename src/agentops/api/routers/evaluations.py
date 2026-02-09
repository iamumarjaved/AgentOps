import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.api.middleware.auth import AuthDep
from agentops.api.schemas.requests import EvaluationTrigger
from agentops.api.schemas.responses import EvaluationResultResponse, EvaluationSummaryResponse
from agentops.db.engine import get_session
from agentops.db.repositories.evaluations import EvaluationResultRepository
from agentops.db.repositories.runs import RunRepository
from agentops.workers.tasks import run_evaluation

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/trigger", status_code=202)
async def trigger_evaluation(
    body: EvaluationTrigger,
    auth: AuthDep,
    session: AsyncSession = Depends(get_session),
):
    """Trigger quality evaluation for a completed run."""
    repo = RunRepository(session)
    run = await repo.get_by_id(uuid.UUID(body.run_id))
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status != "completed":
        raise HTTPException(status_code=400, detail="Can only evaluate completed runs")

    run_evaluation.delay(body.run_id, body.scorers)
    return {"message": "Evaluation queued", "run_id": body.run_id}


@router.get("/summary", response_model=EvaluationSummaryResponse)
async def evaluation_summary(
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get aggregated evaluation scores."""
    repo = EvaluationResultRepository(session)
    avg_scores = await repo.get_average_scores()

    total = sum(1 for _ in avg_scores)  # simplified count
    return EvaluationSummaryResponse(average_scores=avg_scores, total_evaluations=total)


@router.get("/{run_id}", response_model=list[EvaluationResultResponse])
async def get_evaluation_results(
    run_id: uuid.UUID,
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """Get evaluation results for a specific run."""
    repo = EvaluationResultRepository(session)
    results = await repo.get_for_run(run_id)
    return [EvaluationResultResponse.model_validate(r) for r in results]
