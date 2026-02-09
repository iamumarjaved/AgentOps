import asyncio
import json
import time
import uuid

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from agentops.config import settings
from agentops.observability.logger import get_logger
from agentops.observability.metrics import active_runs, run_latency_seconds, runs_total
from agentops.workers.celery_app import celery_app

logger = get_logger("workers")


def _get_sync_session() -> Session:
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(settings.database_url_sync)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def _publish_event(run_id: str, event_type: str, data: dict) -> None:
    """Publish event to Redis pub/sub."""
    try:
        r = redis.from_url(settings.redis_url)
        event = {"type": event_type, "run_id": run_id, "timestamp": time.time(), **data}
        r.publish(f"agentops:run:{run_id}", json.dumps(event))
        r.close()
    except Exception:
        pass


@celery_app.task(bind=True, name="agentops.run_pipeline")
def run_pipeline(self, run_id: str, topic: str, config: dict | None = None):
    """Execute the agent pipeline asynchronously."""
    logger.info("pipeline_started", run_id=run_id, topic=topic)
    active_runs.inc()

    session = _get_sync_session()
    start_time = time.time()

    try:
        from agentops.db.models import Run
        run = session.get(Run, uuid.UUID(run_id))
        if not run:
            raise ValueError(f"Run {run_id} not found")

        run.status = "running"
        run.started_at = __import__("datetime").datetime.utcnow()
        session.commit()

        _publish_event(run_id, "run_started", {"topic": topic})

        # Run the async agent pipeline
        from agentops.agents.graph import compile_and_run
        from agentops.observability.callbacks import ObservabilityCallbackHandler

        import redis as sync_redis
        redis_client = None
        try:
            import redis.asyncio as aioredis
            redis_client = aioredis.from_url(settings.redis_url)
        except Exception:
            pass

        callback = ObservabilityCallbackHandler(run_id=run_id, redis_client=redis_client)
        result = asyncio.run(compile_and_run(topic, config, callbacks=[callback]))

        # Update run with results
        duration = time.time() - start_time
        run.status = "completed"
        run.result = result.get("report", "")
        run.total_tokens = callback.token_tracker.total_tokens
        run.total_cost_usd = callback.token_tracker.total_cost_usd
        run.total_latency_seconds = duration
        run.completed_at = __import__("datetime").datetime.utcnow()
        session.commit()

        # Update metrics
        runs_total.labels(status="completed").inc()
        run_latency_seconds.observe(duration)

        _publish_event(run_id, "run_completed", {
            "total_tokens": callback.token_tracker.total_tokens,
            "total_cost_usd": callback.token_tracker.total_cost_usd,
            "latency_seconds": duration,
        })

        logger.info(
            "pipeline_completed",
            run_id=run_id,
            duration=round(duration, 2),
            tokens=callback.token_tracker.total_tokens,
            cost=callback.token_tracker.total_cost_usd,
        )

    except Exception as e:
        duration = time.time() - start_time
        runs_total.labels(status="failed").inc()

        try:
            run = session.get(Run, uuid.UUID(run_id))
            if run:
                run.status = "failed"
                run.error = str(e)[:2000]
                run.total_latency_seconds = duration
                run.completed_at = __import__("datetime").datetime.utcnow()
                session.commit()
        except Exception:
            session.rollback()

        _publish_event(run_id, "run_failed", {"error": str(e)})
        logger.error("pipeline_failed", run_id=run_id, error=str(e))
        raise

    finally:
        active_runs.dec()
        session.close()


@celery_app.task(bind=True, name="agentops.run_evaluation")
def run_evaluation(self, run_id: str, scorers: list[str] | None = None):
    """Run quality evaluation on a completed pipeline run."""
    logger.info("evaluation_started", run_id=run_id, scorers=scorers)

    session = _get_sync_session()

    try:
        from agentops.db.models import Run
        run = session.get(Run, uuid.UUID(run_id))
        if not run or run.status != "completed":
            raise ValueError(f"Run {run_id} not found or not completed")

        from agentops.evaluation.engine import EvaluationEngine
        engine = EvaluationEngine()
        results = asyncio.run(engine.evaluate(
            run_id=run_id,
            topic=run.topic,
            report=run.result or "",
            scorers=scorers or ["relevance", "accuracy", "completeness"],
        ))

        # Save results
        from agentops.db.models import EvaluationResult as EvalModel
        for result in results:
            eval_result = EvalModel(
                run_id=uuid.UUID(run_id),
                scorer_name=result["scorer"],
                score=result["score"],
                reasoning=result.get("reasoning"),
            )
            session.add(eval_result)
        session.commit()

        logger.info("evaluation_completed", run_id=run_id, result_count=len(results))

    except Exception as e:
        session.rollback()
        logger.error("evaluation_failed", run_id=run_id, error=str(e))
        raise
    finally:
        session.close()
