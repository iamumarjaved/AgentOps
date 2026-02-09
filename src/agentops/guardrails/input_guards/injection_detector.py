import re

from agentops.observability.logger import get_logger

logger = get_logger("guardrails.injection")

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"forget\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"new\s+instructions?\s*:",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"override\s+(system|safety)",
    r"jailbreak",
    r"do\s+anything\s+now",
    r"act\s+as\s+if\s+you\s+have\s+no\s+(restrictions|limits|rules)",
]


class InjectionDetector:
    """Detects prompt injection attempts in user input."""

    def __init__(self, custom_patterns: list[str] | None = None):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
        if custom_patterns:
            self.patterns.extend(re.compile(p, re.IGNORECASE) for p in custom_patterns)

    def detect(self, text: str) -> dict:
        """Check text for injection patterns."""
        matches = []
        for pattern in self.patterns:
            found = pattern.findall(text)
            if found:
                matches.append({
                    "pattern": pattern.pattern,
                    "matches": [str(m) for m in found],
                })

        if matches:
            logger.warning("injection_detected", match_count=len(matches))

        return {
            "is_injection": bool(matches),
            "matches": matches,
            "severity": "critical" if matches else "low",
        }
