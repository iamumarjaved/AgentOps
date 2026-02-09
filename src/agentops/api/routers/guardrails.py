from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.api.middleware.auth import AuthDep
from agentops.api.schemas.requests import GuardrailCheck
from agentops.api.schemas.responses import ViolationResponse
from agentops.db.engine import get_session
from agentops.db.repositories.guardrails import GuardrailViolationRepository
from agentops.guardrails.engine import GuardrailEngine

router = APIRouter(prefix="/guardrails", tags=["guardrails"])


@router.get("/violations", response_model=list[ViolationResponse])
async def list_violations(
    guard_type: str | None = None,
    direction: str | None = None,
    severity: str | None = None,
    limit: int = 50,
    offset: int = 0,
    auth: AuthDep = None,
    session: AsyncSession = Depends(get_session),
):
    """List guardrail violations with optional filters."""
    repo = GuardrailViolationRepository(session)
    violations = await repo.list_violations(
        guard_type=guard_type,
        direction=direction,
        severity=severity,
        limit=limit,
        offset=offset,
    )
    return [ViolationResponse.model_validate(v) for v in violations]


@router.post("/check")
async def check_content(
    body: GuardrailCheck,
    auth: AuthDep,
):
    """Check text against guardrails (for testing)."""
    engine = GuardrailEngine()
    if body.direction == "input":
        result = await engine.check_input(body.text)
    else:
        result = await engine.check_output(body.text)

    return {
        "passed": result.passed,
        "action": result.action,
        "violations": result.violations,
        "sanitized_text": result.sanitized_text,
    }
