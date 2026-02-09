"""Celery background workers for async pipeline and evaluation execution."""

from agentops.workers.celery_app import celery_app

__all__ = ["celery_app"]
