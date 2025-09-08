from typing import List
from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession
from app.core.database import get_db
from app.repositories.car_repository import CarRepository
from app.api.cars.car_schema import CarCreate, CarUpdate, CarResponse
from app.core.security import get_current_user
import uuid

router = APIRouter()


async def fetch_car_or_404(car_id: str, session: AsyncSession) -> dict:
    repo = CarRepository(session)
    car_record = await repo.get_car(car_id)
    if not car_record:
        raise HTTPException(status_code=404, detail="Car not found")
    return car_record


@router.post("/", response_model=CarResponse)
async def create_car(
    car_data: CarCreate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    car_id = str(uuid.uuid4())
    await repo.create_make(car_data.make_name)
    await repo.create_model(car_data.model_name, car_data.make_name)
    car_record = await repo.create_car(
        car_id, car_data.year, car_data.model_name, car_data.make_name
    )
    if not car_record:
        raise HTTPException(status_code=500, detail="Failed to create car")
    return car_record


@router.get("/", response_model=List[CarResponse])
async def list_cars(
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    return await repo.list_cars(limit)


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await fetch_car_or_404(car_id, session)


@router.put("/{car_id}", response_model=CarResponse)
async def replace_car(
    car_id: str,
    car_data: CarCreate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    car_record = await repo.replace_car(car_id, car_data)
    if not car_record:
        raise HTTPException(status_code=500, detail="Failed to replace car")
    return car_record


@router.patch("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: str,
    update_data: CarUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    car_record = await repo.update_car(car_id, update_data)
    if not car_record:
        raise HTTPException(status_code=404, detail="Car not found during update")
    return car_record


@router.delete("/{car_id}")
async def delete_car(
    car_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    result = await repo.delete_car(car_id)
    if not result:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"detail": f"Car {car_id} deleted successfully"}
