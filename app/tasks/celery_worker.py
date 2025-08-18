import os
import logging
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
    include=["app.tasks.sync_cars"],
)

celery.conf.update(
    timezone="UTC",
    broker_url=broker_url,
    result_backend=result_backend,
)

celery.conf.beat_schedule = {
    "sync_cars_every_5_minutes": {
        "task": "app.tasks.sync_cars.sync_all_cars",
        "schedule": crontab(minute="*/5"),
    },
}

DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URI")
if not DATABASE_URL:
    raise RuntimeError(
        "Missing required environment variable: SQLALCHEMY_DATABASE_URI"
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.exception("DB session error: %s", e)
        db.rollback()
        raise
    finally:
        db.close()
