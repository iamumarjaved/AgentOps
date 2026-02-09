"""Prompt templates for each agent in the research pipeline."""

from agentops.agents.prompts.templates import (
    FACT_CHECKER_PROMPT,
    REPORT_WRITER_PROMPT,
    RESEARCHER_PROMPT,
    SUMMARIZER_PROMPT,
    SUPERVISOR_PROMPT,
)

__all__ = [
    "SUPERVISOR_PROMPT",
    "RESEARCHER_PROMPT",
    "SUMMARIZER_PROMPT",
    "FACT_CHECKER_PROMPT",
    "REPORT_WRITER_PROMPT",
]
