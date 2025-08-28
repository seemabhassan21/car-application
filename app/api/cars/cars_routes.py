from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core import get_async_session
from app.core.security import get_current_user
from app.models.cars import Car, CarModel
from app.api.cars.car_schema import CarCreate, CarUpdate, CarRead
from app.utils.common import cursor_paginate, CursorPage
from app.utils.services import (
    fetch_car,
    update_car_model_fields,
    db_commit_retry,
    create_car_with_model,
)

router = APIRouter()


@router.post("/", response_model=CarRead, status_code=status.HTTP_201_CREATED)
@db_commit_retry()
async def create_car(
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await create_car_with_model(
        session=session,
        car_model_id=payload.car_model_id,
        name=payload.name,
        year=payload.year,
        make_name=payload.make,
    )
    await session.refresh(car)
    return await fetch_car(session, car.id)


@router.get("/", response_model=CursorPage[CarRead])
async def list_cars(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    limit: int = 10,
    cursor: Optional[int] = None,
):
    query = select(Car).options(selectinload(Car.car_model).selectinload(CarModel.make))
    return await cursor_paginate(query, session, model_id_field="id", limit=limit, cursor=cursor)


@router.get("/{car_id}", response_model=CarRead)
async def get_car(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    car = await fetch_car(session, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.patch("/{car_id}", response_model=CarRead)
@db_commit_retry()
async def patch_car(
    car_id: int,
    payload: CarUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await fetch_car(session, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    update_data = payload.model_dump(exclude_unset=True)
    await update_car_model_fields(
        session,
        car.car_model_id,
        name=update_data.get("name"),
        year=update_data.get("year"),
        make_name=update_data.get("make"),
    )
    return await fetch_car(session, car.id)


@router.put("/{car_id}", response_model=CarRead)
@db_commit_retry()
async def put_car(
    car_id: int,
    payload: CarCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await fetch_car(session, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # re-use same service function
    new_car = await create_car_with_model(
        session=session,
        car_model_id=payload.car_model_id,
        name=payload.name,
        year=payload.year,
        make_name=payload.make,
    )

    car.car_model_id = new_car.car_model_id
    await session.flush()
    await session.refresh(car)
    return await fetch_car(session, car.id)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
@db_commit_retry()
async def delete_car(
    car_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: dict = Depends(get_current_user),
):
    car = await fetch_car(session, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    await session.delete(car)
    return None
