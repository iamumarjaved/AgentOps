import time
from typing import Any
from uuid import UUID

import redis.asyncio as aioredis
import json

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from agentops.observability.logger import get_logger
from agentops.observability.metrics import (
    agent_step_latency_seconds,
    cost_usd_total,
    tokens_total,
)
from agentops.observability.token_tracker import TokenTracker

logger = get_logger("callbacks")


class ObservabilityCallbackHandler(AsyncCallbackHandler):
    """Callback handler that tracks tokens, cost, latency, and publishes events."""

    def __init__(
        self,
        run_id: str,
        redis_client: aioredis.Redis | None = None,
    ):
        self.run_id = run_id
        self.redis = redis_client
        self.token_tracker = TokenTracker()
        self._step_starts: dict[str, float] = {}
        self._current_agent: str = "unknown"
        self.step_metrics: list[dict] = []

    def set_current_agent(self, agent_name: str) -> None:
        self._current_agent = agent_name

    async def on_llm_start(self, serialized: dict[str, Any], prompts: list[str],
                           *, run_id: UUID, **kwargs: Any) -> None:
        self._step_starts[str(run_id)] = time.time()
        await self._publish_event("llm_start", {
            "agent": self._current_agent,
            "model": serialized.get("kwargs", {}).get("model_name", "gpt-4o"),
        })

    async def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        duration = time.time() - self._step_starts.pop(str(run_id), time.time())

        # Extract token usage
        usage = response.llm_output or {}
        token_usage = usage.get("token_usage", {})
        input_tokens = token_usage.get("prompt_tokens", 0)
        output_tokens = token_usage.get("completion_tokens", 0)

        # Track costs
        cost_info = self.token_tracker.record_usage(input_tokens, output_tokens)

        # Update Prometheus metrics
        agent_step_latency_seconds.labels(agent_name=self._current_agent).observe(duration)
        tokens_total.labels(agent_name=self._current_agent, direction="input").inc(input_tokens)
        tokens_total.labels(agent_name=self._current_agent, direction="output").inc(output_tokens)
        cost_usd_total.labels(agent_name=self._current_agent).inc(cost_info["total_cost_usd"])

        step_metric = {
            "agent": self._current_agent,
            "latency_seconds": round(duration, 4),
            **cost_info,
        }
        self.step_metrics.append(step_metric)

        logger.info(
            "llm_call_completed",
            run_id=self.run_id,
            agent=self._current_agent,
            latency=round(duration, 4),
            **cost_info,
        )

        await self._publish_event("llm_end", step_metric)

    async def on_tool_start(self, serialized: dict[str, Any], input_str: str,
                            *, run_id: UUID, **kwargs: Any) -> None:
        self._step_starts[str(run_id)] = time.time()
        tool_name = serialized.get("name", "unknown")
        await self._publish_event("tool_start", {
            "agent": self._current_agent,
            "tool": tool_name,
        })

    async def on_tool_end(self, output: str, *, run_id: UUID, **kwargs: Any) -> None:
        duration = time.time() - self._step_starts.pop(str(run_id), time.time())
        await self._publish_event("tool_end", {
            "agent": self._current_agent,
            "latency_seconds": round(duration, 4),
        })

    async def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        logger.error("llm_error", run_id=self.run_id, agent=self._current_agent, error=str(error))
        await self._publish_event("llm_error", {
            "agent": self._current_agent,
            "error": str(error),
        })

    async def _publish_event(self, event_type: str, data: dict) -> None:
        """Publish event to Redis pub/sub for WebSocket streaming."""
        if self.redis:
            event = {
                "type": event_type,
                "run_id": self.run_id,
                "timestamp": time.time(),
                **data,
            }
            try:
                await self.redis.publish(
                    f"agentops:run:{self.run_id}",
                    json.dumps(event),
                )
            except Exception:
                pass  # Non-critical: don't fail the pipeline for pub/sub issues
