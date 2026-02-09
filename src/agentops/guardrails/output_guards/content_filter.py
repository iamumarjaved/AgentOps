import re

from agentops.observability.logger import get_logger

logger = get_logger("guardrails.content_filter")

# Patterns for content that should not appear in research reports
FILTERED_PATTERNS = [
    r"(?:as an ai|as a language model|i cannot|i don't have access)",
    r"(?:i apologize|sorry,?\s+(?:but\s+)?i\s+(?:can't|cannot))",
    r"(?:my training data|my knowledge cutoff)",
]


class ContentFilter:
    """Filters unwanted patterns from output text."""

    def __init__(self, custom_patterns: list[str] | None = None):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in FILTERED_PATTERNS]
        if custom_patterns:
            self.patterns.extend(re.compile(p, re.IGNORECASE) for p in custom_patterns)

    def filter(self, text: str) -> dict:
        """Check text for unwanted content patterns."""
        matches = []
        for pattern in self.patterns:
            found = pattern.findall(text)
            if found:
                matches.append({
                    "pattern": pattern.pattern,
                    "matches": [str(m) for m in found],
                })

        if matches:
            logger.warning("content_filtered", match_count=len(matches))

        return {
            "has_filtered_content": bool(matches),
            "matches": matches,
        }
