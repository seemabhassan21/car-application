from pydantic import BaseModel, Field
from typing import Optional, List


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

    class Config:
        from_attributes = True

    @classmethod
    def from_repo(cls, data: dict):
        return cls(
            id=data["car"]["id"],
            year=data["car"]["year"],
            make=data["make"]["name"],
            model=data["model"]["name"],
        )


class CarListResponse(BaseModel):
    cars: List[CarResponse]

    @classmethod
    def from_repo_list(cls, records: list):
        return cls(cars=[CarResponse.from_repo(r) for r in records])
