import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

celery = Celery(
    "carapp",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery.conf.update(
    timezone="UTC",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        "sync_cars_every_5min": {
            "task": "app.tasks.sync_cars.sync_cars",
            "schedule": crontab(minute="*/5"),
        },
    },
)

import app.tasks.sync_cars
