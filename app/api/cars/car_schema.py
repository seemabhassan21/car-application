from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CarBase(BaseModel):
    car_model_id: Optional[int] = None
    name: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None


class CarCreate(BaseModel):
    car_model_id: int = Field(..., description="ID of the car model")
    name: str = Field(..., description="Car model name")
    year: int = Field(..., ge=1990, le=2026)
    make: str = Field(..., description="Car make")


class CarUpdate(CarBase):
    pass


class MakeRead(BaseModel):
    id: int
    name: str


class CarModelRead(BaseModel):
    id: int
    name: str
    year: int
    make: MakeRead
    full_name: str

    class Config:
        orm_mode = True


class CarRead(BaseModel):
    id: int
    car_model_id: int
    car_model: CarModelRead
    created_at: datetime
    full_name: str

    class Config:
        orm_mode = True
