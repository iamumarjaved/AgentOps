import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agentops.db.models import Run, AgentStep


class RunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, topic: str, config: dict | None = None, variant: str | None = None,
                     ab_test_id: uuid.UUID | None = None) -> Run:
        run = Run(
            topic=topic,
            config=config or {},
            variant=variant,
            ab_test_id=ab_test_id,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_by_id(self, run_id: uuid.UUID) -> Run | None:
        result = await self.session.execute(
            select(Run)
            .options(selectinload(Run.steps), selectinload(Run.violations))
            .where(Run.id == run_id)
        )
        return result.scalar_one_or_none()

    async def list_runs(
        self, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Run]:
        query = select(Run).order_by(Run.created_at.desc()).limit(limit).offset(offset)
        if status:
            query = query.where(Run.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(self, run_id: uuid.UUID, status: str, **kwargs: object) -> None:
        run = await self.session.get(Run, run_id)
        if run:
            run.status = status  # type: ignore[assignment]
            for key, value in kwargs.items():
                setattr(run, key, value)
            if status == "running" and not run.started_at:
                run.started_at = datetime.utcnow()
            if status in ("completed", "failed"):
                run.completed_at = datetime.utcnow()

    async def update_metrics(self, run_id: uuid.UUID, tokens: int, cost: float,
                             latency: float) -> None:
        run = await self.session.get(Run, run_id)
        if run:
            run.total_tokens += tokens  # type: ignore[operator]
            run.total_cost_usd += cost  # type: ignore[operator]
            run.total_latency_seconds = latency  # type: ignore[assignment]

    async def count_by_status(self) -> dict[str, int]:
        result = await self.session.execute(
            select(Run.status, func.count(Run.id)).group_by(Run.status)
        )
        return {row[0]: row[1] for row in result.all()}


class AgentStepRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, run_id: uuid.UUID, agent_name: str, step_order: int) -> AgentStep:
        step = AgentStep(run_id=run_id, agent_name=agent_name, step_order=step_order)
        self.session.add(step)
        await self.session.flush()
        return step

    async def update(self, step_id: uuid.UUID, **kwargs: object) -> None:
        step = await self.session.get(AgentStep, step_id)
        if step:
            for key, value in kwargs.items():
                setattr(step, key, value)

    async def get_steps_for_run(self, run_id: uuid.UUID) -> list[AgentStep]:
        result = await self.session.execute(
            select(AgentStep)
            .where(AgentStep.run_id == run_id)
            .order_by(AgentStep.step_order)
        )
        return list(result.scalars().all())
