import os
from typing import Any, Dict, Optional, List
from uuid import uuid4
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()
NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD = os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")
if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    raise RuntimeError("Missing Neo4j connection details in .env")

driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


async def run_query(query: str, params: Optional[Dict[str, Any]] = None):
    async with driver.session() as session:
        return [record.data() async for record in await session.run(query, params or {})]


FIELD_ALIASES = {"make_name": "make", "model_name": "model"}
SUPPORTED_FIELDS = {"car", "make", "model", "year"}


def build_projections(fields: Optional[List[str]]) -> str:
    if not fields:
        return "c {.*, year: c.year} AS car, cm.name AS model, m.name AS make"
    proj_map = {
        "car": "c {.*, year: c.year} AS car",
        "model": "cm.name AS model",
        "make": "m.name AS make",
        "year": "c.year AS year"
    }
    normalized = [FIELD_ALIASES.get(f, f) for f in fields if f in SUPPORTED_FIELDS]
    projections = [proj_map[f] for f in normalized if f != "year" or "car" not in normalized]
    return ", ".join(projections) or "c {.*, year: c.year} AS car, cm.name AS model, m.name AS make"


async def create_car(make_name: str, model_name: str, year: int):
    query = """
    MERGE (m:Make {name: $make_name})
    MERGE (cm:CarModel {name: $model_name})-[:BELONGS_TO]->(m)
    CREATE (c:Car {id: $id, year: $year})
    MERGE (c)-[:INSTANCE_OF]->(cm)
    RETURN c {.*, year: c.year} AS car, cm.name AS model, m.name AS make
    """
    return await run_query(query, {"id": str(uuid4()), "year": year, "make_name": make_name, "model_name": model_name})


async def get_car_by_id(car_id: str, fields: Optional[List[str]] = None):
    query = f"""
    MATCH (c:Car {{id: $car_id}})-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make)
    RETURN {build_projections(fields)}
    """
    return await run_query(query, {"car_id": car_id})


async def list_cars(make_name: Optional[str] = None, model_name: Optional[str] = None, year: Optional[int] = None,
                    fields: Optional[List[str]] = None, limit: int = 10, cursor: Optional[str] = None):
    query = "MATCH (c:Car)-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make) WHERE 1=1 "
    params = {k: v for k, v in [("make_name", make_name), ("model_name", model_name), ("year", year), ("cursor", cursor)] if v is not None}
    if cursor:
        query += "AND c.id > $cursor "
    if make_name:
        query += "AND m.name = $make_name "
    if model_name:
        query += "AND cm.name = $model_name "
    if year is not None:
        query += "AND c.year = $year "

    projections = build_projections(fields)
    if fields and len(fields) == 1:
        projections = f"DISTINCT {projections}"
    query += f"RETURN {projections} ORDER BY c.id ASC LIMIT $limit"
    params["limit"] = limit
    return await run_query(query, params)


async def update_car(car_id: str, year: Optional[int] = None, make_name: Optional[str] = None, model_name: Optional[str] = None):
    if not await get_car_by_id(car_id):
        return []

    if year is not None:
        await run_query("MATCH (c:Car {id: $id}) SET c.year = $year", {"id": car_id, "year": year})

    if make_name or model_name:
        query_parts = ["MATCH (c:Car {id: $id})-[r:INSTANCE_OF]->(oldModel:CarModel)-[:BELONGS_TO]->(oldMake:Make)"]
        params = {"id": car_id, **({} if make_name is None else {"make_name": make_name}), **({} if model_name is None else {"model_name": model_name})}
        if make_name: query_parts.append("MERGE (newMake:Make {name: $make_name})")
        if model_name: query_parts.append("MERGE (newModel:CarModel {name: $model_name if model_name else oldModel.name})-[:BELONGS_TO]->({ 'newMake' if make_name else 'oldMake'})")
        query_parts.append("MERGE (c)-[:INSTANCE_OF]->(newModel if model_name else oldModel) DELETE r")
        await run_query("\n".join(query_parts), params)

    return await get_car_by_id(car_id)


async def delete_car(car_id: str):
    if not await get_car_by_id(car_id):
        return []
    return await run_query("MATCH (c:Car {id: $car_id}) DETACH DELETE c RETURN $car_id AS deleted_id", {"car_id": car_id})


async def search_cars(filters: Dict[str, Any], fields: Optional[List[str]] = None, limit: int = 10, cursor: Optional[str] = None):
    return await list_cars(make_name=filters.get("make_name"), model_name=filters.get("model_name"),
                           year=filters.get("year"), fields=fields, limit=limit, cursor=cursor)
