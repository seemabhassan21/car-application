from fastapi import APIRouter
from . import cars_routes

router = APIRouter(prefix="/cars", tags=["cars"])
router.include_router(cars_routes.router)

__all__ = ["router"]
