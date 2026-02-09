import time

from agentops.guardrails.input_guards.injection_detector import InjectionDetector
from agentops.guardrails.input_guards.input_validator import InputValidator
from agentops.guardrails.input_guards.pii_detector import PIIDetector
from agentops.guardrails.output_guards.content_filter import ContentFilter
from agentops.guardrails.output_guards.format_validator import FormatValidator
from agentops.guardrails.output_guards.hallucination_flagger import HallucinationFlagger
from agentops.guardrails.output_guards.toxicity_checker import ToxicityChecker
from agentops.observability.logger import get_logger
from agentops.observability.metrics import guardrail_check_latency, guardrail_violations_total

logger = get_logger("guardrails.engine")


class GuardrailResult:
    def __init__(self):
        self.passed = True
        self.action: str = "allowed"
        self.violations: list[dict] = []
        self.sanitized_text: str | None = None

    def add_violation(self, guard_type: str, direction: str, action: str,
                      severity: str, details: dict) -> None:
        self.violations.append({
            "guard_type": guard_type,
            "direction": direction,
            "action": action,
            "severity": severity,
            "details": details,
        })
        if action == "blocked":
            self.passed = False
            self.action = "blocked"
        elif action == "flagged" and self.action != "blocked":
            self.action = "flagged"

        guardrail_violations_total.labels(guard_type=guard_type, action=action).inc()


class GuardrailEngine:
    """Orchestrates all input and output guardrail checks."""

    def __init__(self):
        self.pii_detector = PIIDetector()
        self.injection_detector = InjectionDetector()
        self.input_validator = InputValidator()
        self.toxicity_checker = ToxicityChecker()
        self.hallucination_flagger = HallucinationFlagger()
        self.format_validator = FormatValidator()
        self.content_filter = ContentFilter()

    async def check_input(self, text: str) -> GuardrailResult:
        """Run all input guardrails on the given text."""
        result = GuardrailResult()

        # Input validation
        start = time.time()
        validation = self.input_validator.validate(text)
        guardrail_check_latency.labels(guard_type="input_validator").observe(time.time() - start)
        if not validation["is_valid"]:
            result.add_violation(
                guard_type="input_validator",
                direction="input",
                action="blocked",
                severity="medium",
                details=validation,
            )
            return result

        # Injection detection
        start = time.time()
        injection = self.injection_detector.detect(text)
        guardrail_check_latency.labels(guard_type="injection_detector").observe(time.time() - start)
        if injection["is_injection"]:
            result.add_violation(
                guard_type="injection_detector",
                direction="input",
                action="blocked",
                severity="critical",
                details=injection,
            )
            return result

        # PII detection
        start = time.time()
        pii = self.pii_detector.detect(text)
        guardrail_check_latency.labels(guard_type="pii_detector").observe(time.time() - start)
        if pii["has_pii"]:
            result.add_violation(
                guard_type="pii_detector",
                direction="input",
                action="sanitized",
                severity="high",
                details={"entities": pii["entities"]},
            )
            result.sanitized_text = pii["sanitized_text"]

        return result

    async def check_output(self, text: str, source_material: str = "") -> GuardrailResult:
        """Run all output guardrails on the given text."""
        result = GuardrailResult()

        # Content filtering
        start = time.time()
        content = self.content_filter.filter(text)
        guardrail_check_latency.labels(guard_type="content_filter").observe(time.time() - start)
        if content["has_filtered_content"]:
            result.add_violation(
                guard_type="content_filter",
                direction="output",
                action="flagged",
                severity="low",
                details=content,
            )

        # Format validation
        start = time.time()
        format_check = self.format_validator.validate(text)
        guardrail_check_latency.labels(guard_type="format_validator").observe(time.time() - start)
        if not format_check["is_valid"]:
            result.add_violation(
                guard_type="format_validator",
                direction="output",
                action="flagged",
                severity="low",
                details=format_check,
            )

        # Toxicity check
        start = time.time()
        toxicity = await self.toxicity_checker.check(text)
        guardrail_check_latency.labels(guard_type="toxicity_checker").observe(time.time() - start)
        if toxicity.get("is_toxic"):
            result.add_violation(
                guard_type="toxicity_checker",
                direction="output",
                action="blocked",
                severity="critical",
                details=toxicity,
            )

        # Hallucination check (only if source material available)
        if source_material:
            start = time.time()
            hallucination = await self.hallucination_flagger.check(text, source_material)
            guardrail_check_latency.labels(guard_type="hallucination_flagger").observe(time.time() - start)
            if hallucination.get("has_hallucinations"):
                result.add_violation(
                    guard_type="hallucination_flagger",
                    direction="output",
                    action="flagged",
                    severity="medium",
                    details=hallucination,
                )

        return result
