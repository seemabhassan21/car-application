import os
from typing import Any, Dict, Optional, List
from uuid import uuid4
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    raise RuntimeError("Missing Neo4j connection details in .env")

driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


async def run_query(query: str, parameters: Optional[Dict[str, Any]] = None):
    async with driver.session() as session:
        result = await session.run(query, parameters or {})
        return [record.data() async for record in result]


FIELD_ALIASES = {
    "make_name": "make",
    "model_name": "model",
}

SUPPORTED_FIELDS = {"car", "make", "model", "year"}


def build_projections(fields: Optional[List[str]]) -> str:
    if not fields:
        return "c {.*, year: c.year} AS car, cm.name AS model, m.name AS make"

    normalized = [FIELD_ALIASES.get(f, f) for f in fields if f in SUPPORTED_FIELDS]

    projections = []
    if "car" in normalized:
        projections.append("c {.*, year: c.year} AS car")
    if "model" in normalized:
        projections.append("cm.name AS model")
    if "make" in normalized:
        projections.append("m.name AS make")
    if "year" in normalized and "car" not in normalized:
        projections.append("c.year AS year")

    return (
        ", ".join(projections)
        if projections
        else "c {.*, year: c.year} AS car, cm.name AS model, m.name AS make"
    )


async def create_car(make_name: str, model_name: str, year: int):
    query = """
    MERGE (m:Make {name: $make_name})
    MERGE (cm:CarModel {name: $model_name})-[:BELONGS_TO]->(m)
    CREATE (c:Car {id: $id, year: $year})
    MERGE (c)-[:INSTANCE_OF]->(cm)
    RETURN c {.*, year: c.year} AS car, cm.name AS model, m.name AS make
    """
    params = {
        "id": str(uuid4()),
        "year": int(year),
        "make_name": make_name,
        "model_name": model_name,
    }
    return await run_query(query, params)


async def get_car_by_id(car_id: str, fields: Optional[List[str]] = None):
    projections = build_projections(fields)
    query = f"""
    MATCH (c:Car {{id: $car_id}})-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make)
    RETURN {projections}
    """
    return await run_query(query, {"car_id": car_id})


async def list_cars(
    make_name: Optional[str] = None,
    model_name: Optional[str] = None,
    year: Optional[Any] = None,
    fields: Optional[List[str]] = None,
    limit: Optional[int] = None,  # Changed to Optional
    offset: int = 0,
):
    query = (
        "MATCH (c:Car)-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make) WHERE 1=1 "
    )
    params: Dict[str, Any] = {"offset": offset}  # Removed default limit

    if make_name:
        query += "AND m.name = $make_name "
        params["make_name"] = make_name
    if model_name:
        query += "AND cm.name = $model_name "
        params["model_name"] = model_name
    if year is not None:
        params["year"] = int(year)
        query += "AND c.year = $year "

    projections = build_projections(fields)

    # Deduplicate if only one field requested
    if fields and len(fields) == 1:
        if not projections.strip().upper().startswith("DISTINCT"):
            projections = f"DISTINCT {projections}"

    # Only add LIMIT if explicitly provided
    if limit is not None:
        params["limit"] = limit
        query += f"RETURN {projections} SKIP $offset LIMIT $limit"
    else:
        query += f"RETURN {projections} SKIP $offset"

    return await run_query(query, params)


async def update_car(
    car_id: str,
    year: Optional[Any] = None,
    make_name: Optional[str] = None,
    model_name: Optional[str] = None,
):
    if not await get_car_by_id(car_id):
        return []

    if year is not None:
        await run_query(
            "MATCH (c:Car {id: $id}) SET c.year = $year",
            {"id": car_id, "year": int(year)},
        )

    if make_name or model_name:
        query = ""
        params = {"id": car_id}

        base_query = "MATCH (c:Car {id: $id})-[r:INSTANCE_OF]->(oldModel:CarModel)-[:BELONGS_TO]->(oldMake:Make) "
        
        if make_name:
            params["make_name"] = make_name
        if model_name:
            params["model_name"] = model_name

        if make_name and not model_name:
            query = base_query + '''
            MERGE (newMake:Make {name: $make_name})
            MERGE (newModel:CarModel {name: oldModel.name})-[:BELONGS_TO]->(newMake)
            MERGE (c)-[:INSTANCE_OF]->(newModel)
            DELETE r
            '''
        elif not make_name and model_name:
            query = base_query + '''
            MERGE (newModel:CarModel {name: $model_name})-[:BELONGS_TO]->(oldMake)
            MERGE (c)-[:INSTANCE_OF]->(newModel)
            DELETE r
            '''
        elif make_name and model_name:
            query = base_query + '''
            MERGE (newMake:Make {name: $make_name})
            MERGE (newModel:CarModel {name: $model_name})-[:BELONGS_TO]->(newMake)
            MERGE (c)-[:INSTANCE_OF]->(newModel)
            DELETE r
            '''
        if query:
            await run_query(query, params)

    return await get_car_by_id(car_id)


async def delete_car(car_id: str):
    if not await get_car_by_id(car_id):
        return []

    query = """
    MATCH (c:Car {id: $car_id})
    DETACH DELETE c
    RETURN $car_id AS deleted_id
    """
    return await run_query(query, {"car_id": car_id})


async def search_cars(filters: Dict[str, Any], fields: Optional[List[str]] = None, limit: Optional[int] = None, offset: int = 0):
    return await list_cars(
        make_name=filters.get("make_name"),
        model_name=filters.get("model_name"),
        year=filters.get("year"),
        fields=fields,
        limit=limit,
        offset=offset,
    )
