import asyncio
import httpx
import logging
from app.task.celery_worker import celery_app
from app.core.config import settings
from app.repositories.car_repository import CarRepository
from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)

API_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"


@celery_app.task(name="app.task.sync_cars.sync_cars")
def sync_cars_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sync_cars_logic())
    loop.close()


async def sync_cars_logic():
    driver = None
    try:
        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )

        headers = {
            "X-Parse-Application-Id": settings.CAR_API_ID,
            "X-Parse-Master-Key": settings.CAR_MASTER_KEY,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(API_URL, headers=headers)
            resp.raise_for_status()
            cars_data = resp.json().get("results", [])

        async with driver.session() as session:
            repo = CarRepository(session)
            for car in cars_data:
                make = car.get("Make")
                model = car.get("Model")
                year = car.get("Year")
                vin = car.get("objectId")

                if not all([make, model, year, vin]):
                    logger.warning(f"Skipping car with incomplete data: {car}")
                    continue

                await repo.create_make(make)
                await repo.create_model(model, make)
                await repo.create_car(vin, year, model, make)

        logger.info("Car sync completed: %d cars processed", len(cars_data))

    except Exception as e:
        logger.error(f"An error occurred during car sync: {e}", exc_info=True)
    finally:
        if driver:
            await driver.close()
