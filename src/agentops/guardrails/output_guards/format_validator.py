import re

from agentops.observability.logger import get_logger

logger = get_logger("guardrails.format")


class FormatValidator:
    """Validates that report output meets formatting requirements."""

    REQUIRED_SECTIONS = [
        "Executive Summary",
        "Key Findings",
        "Detailed Analysis",
        "Conclusions",
    ]

    def __init__(self, min_length: int = 200, max_length: int = 50000):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, text: str) -> dict:
        """Validate output format and structure."""
        issues = []

        if len(text) < self.min_length:
            issues.append(f"Output too short ({len(text)} chars, minimum {self.min_length})")

        if len(text) > self.max_length:
            issues.append(f"Output too long ({len(text)} chars, maximum {self.max_length})")

        # Check for required sections
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            if not re.search(rf"#{{1,3}}\s*{re.escape(section)}", text, re.IGNORECASE):
                missing_sections.append(section)

        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")

        # Check for markdown headers
        headers = re.findall(r"^#{1,3}\s+.+", text, re.MULTILINE)
        if len(headers) < 3:
            issues.append("Insufficient document structure (fewer than 3 headers)")

        if issues:
            logger.warning("format_validation_issues", issues=issues)

        return {
            "is_valid": not issues,
            "issues": issues,
            "section_count": len(headers),
            "char_count": len(text),
        }
