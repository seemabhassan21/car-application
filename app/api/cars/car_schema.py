from pydantic import BaseModel, Field
from typing import Optional


class CarCreate(BaseModel):
    year: int = Field(..., ge=2000, description="Manufacturing year")
    make_name: str = Field(..., description="Car brand e.g., Audi")
    model_name: str = Field(..., description="Car model e.g., Q3")


class CarUpdate(BaseModel):
    year: Optional[int] = Field(None, ge=2000, description="Updated year")
    make_name: Optional[str] = Field(None, description="Updated brand")
    model_name: Optional[str] = Field(None, description="Updated model")


class CarResponse(BaseModel):
    id: str
    year: int
    make: str
    model: str
