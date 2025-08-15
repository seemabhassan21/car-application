import logging
import requests
from app.models.car import Car
from app.config import Config
from app.tasks.celery_worker import celery
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def fetch_cars_by_year(year):
    try:
        response = requests.get(
            Config.CAR_API_URL,
            headers=Config.CAR_API_HEADERS,
            params={"year": year},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        logger.error("Error fetching cars for %s: %s", year, e)
        return []


def sync_cars_for_year(year, SessionLocal):
    cars_data = fetch_cars_by_year(year)
    if not cars_data:
        logger.warning("No data returned for %s", year)
        return 0

    inserted_count = 0
    with SessionLocal() as session:
        try:
            for car in cars_data:
                if not session.query(Car).filter_by(objectId=car["objectId"]).first():
                    session.add(Car(**car))
                    inserted_count += 1
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("DB error inserting cars for %s: %s", year, e)

    logger.info("Inserted %d cars for %s", inserted_count, year)
    return inserted_count


@celery.task
def sync_all_cars():
    from app.tasks.celery_worker import SessionLocal

    inserted_total = 0
    for year in range(2000, 2025):
        inserted_total += sync_cars_for_year(year, SessionLocal)
    logger.info("Total cars inserted: %d", inserted_total)
    return inserted_total
