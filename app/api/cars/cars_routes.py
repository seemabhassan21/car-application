from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import get_async_session
from app.core.security import get_current_user
from app.models import Car, CarModel
from app.api.cars.car_schema import CarCreate, CarUpdate, CarRead
from app.utils.common import cursor_paginate, CursorPage
from app.utils.services import fetch_car, get_car_or_404, validate_car_model

router = APIRouter()


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
async def create_car(
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    await validate_car_model(session, payload.car_model_id)

    car = Car(car_model_id=payload.car_model_id)
    session.add(car)
    await session.commit()
    await session.refresh(car)

    # Update nested fields
    if car.car_model:
        car.car_model.name = payload.name
        car.car_model.year = payload.year
        car.car_model.make.name = payload.make
        await session.commit()
        await session.refresh(car)

    return await fetch_car(session, car.id)


@router.get("/", response_model=CursorPage[CarRead])
async def list_cars(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    limit: int = 10,
    cursor: Optional[int] = None,
):
    query = select(Car).options(
        selectinload(Car.car_model).selectinload(CarModel.make)
    )
    return await cursor_paginate(
        query, session, model_id_field="id", limit=limit, cursor=cursor
    )


@router.get("/{car_id}", response_model=CarRead)
async def get_car(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    car = await fetch_car(session, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.patch("/{car_id}", response_model=CarRead)
async def patch_car(
    car_id: int,
    payload: CarUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await get_car_or_404(session, car_id)
    update_data = payload.model_dump(exclude_unset=True)

    if car_model_id := update_data.get("car_model_id"):
        await validate_car_model(session, car_model_id)
        car.car_model_id = car_model_id

    if car.car_model:
        if name := update_data.get("name"):
            car.car_model.name = name
        if year := update_data.get("year"):
            car.car_model.year = year
        if make := update_data.get("make"):
            car.car_model.make.name = make

    await session.commit()
    await session.refresh(car)
    return await fetch_car(session, car.id)


@router.put("/{car_id}", response_model=CarRead)
async def put_car(
    car_id: int,
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await get_car_or_404(session, car_id)
    await validate_car_model(session, payload.car_model_id)

    car.car_model_id = payload.car_model_id

    # Full replacement of nested fields
    if car.car_model:
        car.car_model.name = payload.name
        car.car_model.year = payload.year
        car.car_model.make.name = payload.make

    await session.commit()
    await session.refresh(car)
    return await fetch_car(session, car.id)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await get_car_or_404(session, car_id)
    await session.delete(car)
    await session.commit()
    return None
