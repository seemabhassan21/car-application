from fastapi import APIRouter

from app.api.auth.auth_routes import router as auth_router
from app.api.cars.cars_routes import router as cars_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="", tags=["auth"])
api_router.include_router(cars_router, prefix="/cars", tags=["cars"])
