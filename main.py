from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import router as api_router
from app.core.database import close_driver


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_driver()

app = FastAPI(title="Car API with Neo4j", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the Car API"}

app.include_router(api_router)
