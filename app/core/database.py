from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)

from .config import settings

Base = declarative_base()

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
