import os
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "carbase-tasks",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks.sync_cars"]
)

celery.conf.update(
    broker_url=broker_url,
    result_backend=result_backend,
    timezone="UTC"
)

celery.conf.beat_schedule = {
    "sync_cars_every_5_minutes": {
        "task": "app.tasks.sync_cars.sync_cars",
        "schedule": crontab(minute="*/5"),
    }
}

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URI")
if not DATABASE_URL:
    raise RuntimeError("Missing required environment variable: SQLALCHEMY_DATABASE_URI")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
