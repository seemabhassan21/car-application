from fastapi import APIRouter
from . import car_routes

router = APIRouter(prefix="/cars", tags=["cars"])
router.include_router(car_routes.router)

__all__ = ["router"]
