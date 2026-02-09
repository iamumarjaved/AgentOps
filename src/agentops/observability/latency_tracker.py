import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class LatencyRecord:
    agent_name: str
    start_time: float
    end_time: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return round(self.end_time - self.start_time, 4)


class LatencyTracker:
    """Tracks latency for agent steps and overall runs."""

    def __init__(self):
        self.records: list[LatencyRecord] = []
        self._run_start: float = 0.0

    def start_run(self) -> None:
        self._run_start = time.time()

    @contextmanager
    def track_step(self, agent_name: str):
        record = LatencyRecord(agent_name=agent_name, start_time=time.time())
        try:
            yield record
        finally:
            record.end_time = time.time()
            self.records.append(record)

    @property
    def total_run_latency(self) -> float:
        if not self._run_start:
            return 0.0
        return round(time.time() - self._run_start, 4)

    def get_step_latencies(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for record in self.records:
            result[record.agent_name] = record.duration_seconds
        return result
