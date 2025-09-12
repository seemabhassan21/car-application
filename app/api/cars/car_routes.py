from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import AsyncSession
import uuid

from app.core.database import get_db
from app.repositories.car_repository import CarRepository
from app.api.cars.car_schema import CarCreate, CarUpdate, CarResponse
from app.core.security import get_current_user

router = APIRouter()

def flatten_car(record: dict) -> dict:
    return {
        "id": record["car"]["id"],
        "year": record["car"]["year"],
        "make": record["make"]["name"],
        "model": record["model"]["name"],
    }

async def fetch_car_or_404(car_id: str, session: AsyncSession) -> dict:
    repo = CarRepository(session)
    car_record = await repo.get_car(car_id)
    if not car_record:
        raise HTTPException(status_code=404, detail="Car not found")
    return flatten_car(car_record)

@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    car_data: CarCreate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    car_id = str(uuid.uuid4())
    try:
        car_record = await repo.create_car(
            car_id, car_data.year, car_data.model, car_data.make
        )
        if not car_record:
            raise HTTPException(status_code=500, detail="Failed to create car")
        return flatten_car(car_record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CarResponse])
async def list_cars(
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    cars = await repo.list_cars(limit)
    return [flatten_car(c) for c in cars]

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
    try:
        car_record = await repo.replace_car(car_id, car_data)
        if not car_record:
            raise HTTPException(status_code=500, detail="Failed to replace car")
        return flatten_car(car_record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: str,
    update_data: CarUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    repo = CarRepository(session)
    try:
        car_record = await repo.update_car(car_id, update_data)
        if not car_record:
            raise HTTPException(status_code=404, detail="Car not found during update")
        return flatten_car(car_record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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