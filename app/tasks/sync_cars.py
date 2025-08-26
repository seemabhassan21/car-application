import os
import logging
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.cars import Make, CarModel, Car
from app.tasks.celery_worker import celery

DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("ASYNC_DATABASE_URL environment variable is required")

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

EXTERNAL_API_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"


@celery.task(name="app.tasks.sync_cars.sync_cars")
def sync_cars() -> None:
    """Celery task entrypoint for syncing cars from external API."""
    try:
        asyncio.run(sync_all_cars_async())
        logger.info("Car sync completed successfully.")
    except Exception as e:
        logger.exception("Car sync failed: %s", e)
        raise


async def sync_all_cars_async() -> None:
    """Fetch and sync Makes, CarModels, and Cars asynchronously."""
    api_id = os.getenv("CAR_API_ID")
    api_key = os.getenv("CAR_MASTER_KEY")
    if not api_id or not api_key:
        logger.error("Missing CAR_API_ID or CAR_MASTER_KEY environment variables")
        return

    headers = {"X-Parse-Application-Id": api_id, "X-Parse-Master-Key": api_key}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(EXTERNAL_API_URL, headers=headers)
            response.raise_for_status()
            cars_data = response.json().get("results", [])
    except Exception as e:
        logger.exception("Failed to fetch cars data: %s", e)
        return

    new_makes = new_models = new_cars = 0

    async with AsyncSessionLocal() as session:
        try:
            for car_data in cars_data:
                make_name = car_data.get("Make")
                model_name = car_data.get("Model")
                year = car_data.get("Year")

                if not (make_name and model_name and year):
                    continue
                if year < 1990 or year > 2026:
                    logger.warning("Skipping invalid year: %s %s %s", make_name, model_name, year)
                    continue

                result = await session.execute(select(Make).where(Make.name == make_name))
                make = result.scalar_one_or_none()
                if not make:
                    make = Make(name=make_name)
                    session.add(make)
                    await session.flush()
                    new_makes += 1

                result = await session.execute(
                    select(CarModel).where(
                        CarModel.name == model_name,
                        CarModel.year == year,
                        CarModel.make_id == make.id,
                    )
                )
                car_model = result.scalar_one_or_none()
                if not car_model:
                    car_model = CarModel(name=model_name, year=year, make_id=make.id)
                    session.add(car_model)
                    await session.flush()
                    new_models += 1

                car = Car(car_model_id=car_model.id)
                session.add(car)
                new_cars += 1

            await session.commit()
            logger.info(
                "Sync completed. Added: %d makes, %d models, %d cars",
                new_makes, new_models, new_cars,
            )

        except SQLAlchemyError as db_err:
            await session.rollback()
            logger.exception("Database error during sync: %s", db_err)
        except Exception as e:
            await session.rollback()
            logger.exception("Unexpected error during sync: %s", e)
