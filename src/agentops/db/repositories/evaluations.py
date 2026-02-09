import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.db.models import EvaluationResult, ABTest, GroundTruth


class EvaluationResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, run_id: uuid.UUID, scorer_name: str, score: float,
        reasoning: str | None = None, metadata: dict | None = None,
    ) -> EvaluationResult:
        result = EvaluationResult(
            run_id=run_id,
            scorer_name=scorer_name,
            score=score,
            reasoning=reasoning,
            metadata_=metadata,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def get_for_run(self, run_id: uuid.UUID) -> list[EvaluationResult]:
        result = await self.session.execute(
            select(EvaluationResult).where(EvaluationResult.run_id == run_id)
        )
        return list(result.scalars().all())

    async def get_average_scores(self, limit: int = 100) -> dict[str, float]:
        result = await self.session.execute(
            select(
                EvaluationResult.scorer_name, func.avg(EvaluationResult.score)
            ).group_by(EvaluationResult.scorer_name)
        )
        return {row[0]: round(float(row[1]), 4) for row in result.all()}


class ABTestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, variants: list[dict],
                     description: str | None = None) -> ABTest:
        test = ABTest(name=name, variants=variants, description=description)
        self.session.add(test)
        await self.session.flush()
        return test

    async def get_active(self) -> ABTest | None:
        result = await self.session.execute(
            select(ABTest).where(ABTest.is_active.is_(True)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, test_id: uuid.UUID) -> ABTest | None:
        return await self.session.get(ABTest, test_id)


class GroundTruthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_topic(self, topic: str) -> GroundTruth | None:
        result = await self.session.execute(
            select(GroundTruth).where(GroundTruth.topic == topic).limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, topic: str, expected_output: str,
                     metadata: dict | None = None) -> GroundTruth:
        gt = GroundTruth(topic=topic, expected_output=expected_output, metadata_=metadata)
        self.session.add(gt)
        await self.session.flush()
        return gt
