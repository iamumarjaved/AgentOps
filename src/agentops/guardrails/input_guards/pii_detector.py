from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from agentops.observability.logger import get_logger

logger = get_logger("guardrails.pii")

_analyzer: AnalyzerEngine | None = None
_anonymizer: AnonymizerEngine | None = None


def _get_analyzer() -> AnalyzerEngine:
    global _analyzer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
    return _analyzer


def _get_anonymizer() -> AnonymizerEngine:
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _anonymizer


class PIIDetector:
    """Detects and optionally redacts PII from input text using Microsoft Presidio."""

    ENTITY_TYPES = [
        "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
        "US_SSN", "IP_ADDRESS", "IBAN_CODE",
    ]

    def __init__(self, score_threshold: float = 0.7):
        self.score_threshold = score_threshold

    def detect(self, text: str) -> dict:
        """Detect PII in text. Returns detection results."""
        analyzer = _get_analyzer()
        results = analyzer.analyze(
            text=text,
            entities=self.ENTITY_TYPES,
            language="en",
            score_threshold=self.score_threshold,
        )

        if not results:
            return {"has_pii": False, "entities": [], "sanitized_text": text}

        entities = [
            {
                "type": r.entity_type,
                "score": round(r.score, 2),
                "start": r.start,
                "end": r.end,
            }
            for r in results
        ]

        anonymizer = _get_anonymizer()
        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

        logger.warning("pii_detected", entity_count=len(entities), types=[e["type"] for e in entities])

        return {
            "has_pii": True,
            "entities": entities,
            "sanitized_text": anonymized.text,
        }
