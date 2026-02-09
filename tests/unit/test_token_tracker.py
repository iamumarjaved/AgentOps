import pytest

from agentops.observability.token_tracker import TokenTracker


class TestTokenTracker:
    def test_record_usage(self):
        tracker = TokenTracker(model="gpt-4o")
        result = tracker.record_usage(input_tokens=1000, output_tokens=500)

        assert result["input_tokens"] == 1000
        assert result["output_tokens"] == 500
        assert result["total_tokens"] == 1500
        assert result["total_cost_usd"] > 0

    def test_cumulative_tracking(self):
        tracker = TokenTracker(model="gpt-4o")
        tracker.record_usage(100, 50)
        tracker.record_usage(200, 100)

        assert tracker.total_input_tokens == 300
        assert tracker.total_output_tokens == 150
        assert tracker.total_tokens == 450

    def test_cost_calculation(self):
        tracker = TokenTracker(model="gpt-4o")
        # 1M input tokens at $2.50 = $2.50
        result = tracker.record_usage(1_000_000, 0)
        assert abs(result["input_cost_usd"] - 2.50) < 0.01

    def test_output_cost(self):
        tracker = TokenTracker(model="gpt-4o")
        # 1M output tokens at $10.00 = $10.00
        result = tracker.record_usage(0, 1_000_000)
        assert abs(result["output_cost_usd"] - 10.00) < 0.01

    def test_count_tokens(self):
        tracker = TokenTracker(model="gpt-4o")
        count = tracker.count_tokens("Hello, world!")
        assert count > 0
        assert isinstance(count, int)
