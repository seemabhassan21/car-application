import asyncio
import random
import string
from functools import wraps
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.cars import Car, CarModel, Make


def generate_vin(length: int = 17) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def fetch_car(session: AsyncSession, car_id: int) -> Optional[Car]:
    result = await session.execute(
        select(Car)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
        .where(Car.id == car_id)
    )
    return result.scalars().first()


async def validate_car_model(session: AsyncSession, car_model_id: int) -> None:
    car_model = await session.get(CarModel, car_model_id)
    if not car_model:
        raise HTTPException(status_code=404, detail="Car model not found")


async def create_or_get_make(session: AsyncSession, make_name: str) -> Make:
    result = await session.execute(select(Make).where(Make.name == make_name))
    make = result.scalars().first()
    if not make:
        make = Make(name=make_name)
        session.add(make)
        await session.flush()
    return make


async def create_car_with_model(
    session: AsyncSession,
    car_model_id: Optional[int] = None,
    name: Optional[str] = None,
    year: Optional[int] = None,
    make_name: Optional[str] = None
) -> Car:
    if car_model_id:
        car_model = await session.get(CarModel, car_model_id)
        if not car_model:
            raise HTTPException(status_code=404, detail="Car model not found")
    else:
        if not (name and year and make_name):
            raise HTTPException(
                status_code=400,
                detail="Either provide car_model_id OR (name, year, make)"
            )
        make = await create_or_get_make(session, make_name)
        car_model = CarModel(name=name, year=year, make_id=make.id)
        session.add(car_model)
        await session.flush()

    car = Car(vin=generate_vin(), car_model_id=car_model.id)
    session.add(car)
    await session.flush()
    return car


async def update_car_model_fields(
    session: AsyncSession,
    car_model_id: int,
    name: Optional[str] = None,
    year: Optional[int] = None,
    make_name: Optional[str] = None
):
    car_model = await session.get(CarModel, car_model_id)
    if not car_model:
        raise HTTPException(status_code=404, detail="Car model not found")

    if name is not None:
        car_model.name = name
    if year is not None:
        car_model.year = year
    if make_name is not None and car_model.make:
        car_model.make.name = make_name

    await session.flush()


def db_commit_retry(retries: int = 3, delay: float = 0.2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            session: AsyncSession = kwargs.get("session")  # type:ignore
            if session is None:
                raise ValueError("Session must be passed as a keyword argument")

            result = await func(*args, **kwargs)

            for attempt in range(1, retries + 1):
                try:
                    await session.commit()
                    return result
                except OperationalError as e:
                    if "Lock wait timeout exceeded" in str(e):
                        await session.rollback()
                        await asyncio.sleep(delay)
                    else:
                        await session.rollback()
                        raise
            raise Exception("Failed to commit after retries due to lock timeout")
        return wrapper
    return decorator
