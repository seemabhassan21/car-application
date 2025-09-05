from pydantic import BaseModel, EmailStr
from typing import Optional


# Input for registration
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
