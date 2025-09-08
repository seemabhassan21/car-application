from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "car_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone="UTC",
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

from app.task.sync_cars import sync_cars_task

celery_app.conf.beat_schedule = {
    "sync-cars-every-5-min": {
        "task": "app.task.sync_cars.sync_cars",
        "schedule": crontab(minute="*/5"),
    }
}
