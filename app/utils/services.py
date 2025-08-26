from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.cars import Car, CarModel


async def fetch_car(session: AsyncSession, car_id: int) -> Car | None:
    res = await session.execute(
        select(Car)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
        .where(Car.id == car_id)
    )
    return res.scalars().first()


async def get_car_or_404(session: AsyncSession, car_id: int) -> Car:
    res = await session.execute(
        select(Car)
        .options(selectinload(Car.car_model).selectinload(CarModel.make))
        .where(Car.id == car_id)
    )
    car = res.scalars().first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


async def validate_car_model(session: AsyncSession, car_model_id: int) -> None:
    car_model = await session.get(CarModel, car_model_id)
    if not car_model:
        raise HTTPException(status_code=404, detail="Car model not found")
