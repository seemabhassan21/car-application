from fastapi import APIRouter
from . import auth_routes

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(auth_routes.router)

__all__ = ['router']
