from celery import Celery

from agentops.config import settings

celery_app = Celery(
    "agentops",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=600,  # 10 min soft limit
    task_time_limit=660,       # 11 min hard limit
)

celery_app.autodiscover_tasks(["agentops.workers"])
