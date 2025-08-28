from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CarBase(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    car_model_id: Optional[int] = None


class CarCreate(CarBase):
    name: Optional[str] = Field(None, description="Car model name")
    year: Optional[int] = Field(None, ge=1990, le=2026)
    make: Optional[str] = Field(None, description="Car make")
    car_model_id: Optional[int] = Field(None, description="ID of existing car model")


class CarUpdate(CarBase):
    pass


class MakeRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CarModelRead(BaseModel):
    id: int
    name: str
    year: int
    make: MakeRead

    class Config:
        orm_mode = True


class CarRead(BaseModel):
    id: int
    car_model_id: int
    vin: str
    car_model: CarModelRead
    created_at: datetime
    full_name: str

    class Config:
        orm_mode = True
