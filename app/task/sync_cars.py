import asyncio
import httpx
import logging
from typing import AsyncGenerator

from neo4j import AsyncGraphDatabase

from app.task.celery_worker import celery_app
from app.core.config import settings
from app.repositories.car_repository import CarRepository

logger = logging.getLogger(__name__)
API_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"

neo4j_driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
)


async def get_neo4j_session() -> AsyncGenerator:
    async with neo4j_driver.session() as session:
        yield session


@celery_app.task(name="app.task.sync_cars.sync_cars")
def sync_cars():
    asyncio.run(sync_cars_logic())


async def sync_cars_logic():
    headers = {
        "X-Parse-Application-Id": settings.CAR_API_ID,
        "X-Parse-Master-Key": settings.CAR_MASTER_KEY,
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(API_URL, headers=headers)
            resp.raise_for_status()
            cars_data = resp.json().get("results", [])

        async for session in get_neo4j_session():
            repo = CarRepository(session)

            for car in cars_data:
                make, model, year, vin = car.get("Make"), car.get("Model"), car.get("Year"), car.get("objectId")
                if not all([make, model, year, vin]):
                    logger.warning("Skipping incomplete car data: %s", car)
                    continue

                await repo.create_make(make)
                await repo.create_model(model, make)

                try:
                    await repo.create_car(vin, year, model, make)
                except Exception as e:
                    logger.warning("Skipping duplicate car %s: %s", vin, e)

        logger.info("Car sync completed: %d cars processed", len(cars_data))

    except Exception as e:
        logger.error("Error during car sync: %s", e, exc_info=True)
