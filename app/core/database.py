from neo4j import AsyncGraphDatabase
from typing import AsyncGenerator
from app.core.config import settings

driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
)


async def get_db() -> AsyncGenerator:
    async with driver.session() as session:
        yield session


async def close_driver():
    await driver.close()
