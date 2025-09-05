from fastapi import APIRouter
from .user_routes import router as user_router

router = APIRouter(prefix="/users", tags=["users"])
router.include_router(user_router)

__all__ = ["router"]
