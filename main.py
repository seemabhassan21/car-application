from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import api_router
from app.core.database import async_engine, Base
from app.core.security import oauth2_scheme

# Lifespan to initialize DB on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Create FastAPI instance with lifespan
app = FastAPI(
    title="Car API (FastAPI async)",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "auth", "description": "User authentication endpoints"},
        {"name": "cars", "description": "Car CRUD endpoints"}
    ]
)

# Include all routes under /api
app.include_router(api_router, prefix="/api")

# Healthcheck endpoint
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
