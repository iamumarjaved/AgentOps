from agentops.observability.logger import get_logger

logger = get_logger("guardrails.input_validator")


class InputValidator:
    """Validates input text meets basic requirements."""

    def __init__(
        self,
        min_length: int = 3,
        max_length: int = 5000,
        blocked_topics: list[str] | None = None,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.blocked_topics = [t.lower() for t in (blocked_topics or [])]

    def validate(self, text: str) -> dict:
        """Validate input text."""
        errors = []

        if len(text.strip()) < self.min_length:
            errors.append(f"Input too short (minimum {self.min_length} characters)")

        if len(text) > self.max_length:
            errors.append(f"Input too long (maximum {self.max_length} characters)")

        text_lower = text.lower()
        for topic in self.blocked_topics:
            if topic in text_lower:
                errors.append(f"Blocked topic detected: {topic}")

        if errors:
            logger.warning("input_validation_failed", errors=errors)

        return {
            "is_valid": not errors,
            "errors": errors,
        }
