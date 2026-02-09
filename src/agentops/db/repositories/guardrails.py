import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.db.models import GuardrailViolation


class GuardrailViolationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        guard_type: str,
        direction: str,
        action: str,
        severity: str,
        details: dict,
        run_id: uuid.UUID | None = None,
        original_content: str | None = None,
        sanitized_content: str | None = None,
    ) -> GuardrailViolation:
        violation = GuardrailViolation(
            run_id=run_id,
            guard_type=guard_type,
            direction=direction,
            action=action,
            severity=severity,
            details=details,
            original_content=original_content,
            sanitized_content=sanitized_content,
        )
        self.session.add(violation)
        await self.session.flush()
        return violation

    async def list_violations(
        self,
        guard_type: str | None = None,
        direction: str | None = None,
        severity: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GuardrailViolation]:
        query = (
            select(GuardrailViolation)
            .order_by(GuardrailViolation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if guard_type:
            query = query.where(GuardrailViolation.guard_type == guard_type)
        if direction:
            query = query.where(GuardrailViolation.direction == direction)
        if severity:
            query = query.where(GuardrailViolation.severity == severity)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_type(self, since: datetime | None = None) -> dict[str, int]:
        query = select(
            GuardrailViolation.guard_type, func.count(GuardrailViolation.id)
        ).group_by(GuardrailViolation.guard_type)
        if since:
            query = query.where(GuardrailViolation.created_at >= since)
        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}
