from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_session
from app.core.security import security
from app.models.user import User
from .user_schema import UserRegisterSchema, TokenSchema

router = APIRouter()


def generate_tokens(user_id: str) -> dict:
    return {
        "access_token": security.create_access_token(user_id),
        "refresh_token": security.create_refresh_token(user_id),
        "token_type": "bearer",
    }


@router.post("/register", response_model=TokenSchema)
async def register(
    user_in: UserRegisterSchema,
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    result_email = await session.execute(select(User).where(User.email == user_in.email))
    if result_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(username=user_in.username, email=user_in.email)
    new_user.set_password(user_in.password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return generate_tokens(str(new_user.id))


@router.post("/login", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not user.check_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return generate_tokens(str(user.id))
