"""Celery application + monthly parcel-sync beat schedule (spec §5.2).

Start the worker::

    celery -A app.workers.celery_app worker --loglevel=info

Start the beat scheduler (fires the monthly sync)::

    celery -A app.workers.celery_app beat --loglevel=info
"""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "gas",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/New_York",  # East Tennessee local time (spec §5.2)
    enable_utc=False,
)

# Spec §5.2: fire on the 1st of each month at 02:00 local time.
celery_app.conf.beat_schedule = {
    "monthly-parcel-sync": {
        "task": "app.workers.tasks.sync_all_counties",
        "schedule": crontab(
            day_of_month=settings.parcel_sync_cron_day,
            hour=settings.parcel_sync_cron_hour,
            minute=0,
        ),
    },
}
