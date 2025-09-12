from pydantic import BaseModel, Field
from typing import Optional


class CarCreate(BaseModel):
    year: int = Field(..., ge=2000)
    make: str = Field(..., min_length=3, max_length=20)
    model: str = Field(..., min_length=3, max_length=20)


class CarUpdate(BaseModel):
    year: Optional[int] = Field(None, ge=2000)
    make: Optional[str] = Field(None, min_length=3, max_length=20)
    model: Optional[str] = Field(None, min_length=3, max_length=20)

    @classmethod
    def validate(cls, values):
        if not any(values.values()):
            raise ValueError("Provide at least one field")
        return values


class CarResponse(BaseModel):
    id: str
    year: int
    make: str
    model: str
