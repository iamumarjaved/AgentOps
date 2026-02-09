import tiktoken

# GPT-4o pricing per 1M tokens (as of 2024)
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


class TokenTracker:
    """Tracks token usage and calculates costs."""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self._encoding = tiktoken.encoding_for_model(model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self._encoding.encode(text))

    def record_usage(self, input_tokens: int, output_tokens: int) -> dict:
        """Record token usage and return cost breakdown."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        pricing = PRICING.get(self.model, PRICING["gpt-4o"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(input_cost + output_cost, 6),
        }

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_cost_usd(self) -> float:
        pricing = PRICING.get(self.model, PRICING["gpt-4o"])
        input_cost = (self.total_input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.total_output_tokens / 1_000_000) * pricing["output"]
        return round(input_cost + output_cost, 6)
