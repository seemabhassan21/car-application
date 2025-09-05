# app/api/users/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession
from datetime import timedelta

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.api.users.user_schema import UserCreate, UserLogin, UserRead
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    existing = await repo.get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pw = get_password_hash(user.password)
    created = await repo.create_user(user.username, user.email, hashed_pw)
    if not created:
        raise HTTPException(status_code=500, detail="User creation failed")

    return UserRepository.to_public_dict(created)


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    db_user = await repo.get_user_by_username(user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user["id"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
