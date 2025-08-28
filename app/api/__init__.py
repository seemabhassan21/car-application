from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.cars import router as cars_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(cars_router)

__all__ = ["api_router"]
