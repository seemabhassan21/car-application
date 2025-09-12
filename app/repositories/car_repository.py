from neo4j import AsyncSession
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.cars.car_schema import CarUpdate, CarCreate


class CarRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _process_record(self, record):
        if not record:
            return None
        return {k: dict(v) if hasattr(v, 'items') else v for k, v in record.items()}

    async def _run_single(self, query: str, **params):
        result = await self.session.run(query, **params)
        return await self._process_record(await result.single())

    async def _run_query(self, query: str, **params):
        result = await self.session.run(query, **params)
        return [await self._process_record(r) async for r in result]

    async def create_car(self, car_id: str, year: int, model: str, make: str):
        existing = await self._run_single(
            "MATCH (c:Car {make: $make, model: $model, year: $year}) RETURN c LIMIT 1",
            make=make, model=model, year=year
        )
        if existing:
            raise ValueError(f"Car with make '{make}', model '{model}', year {year} already exists")

        query = """
        MERGE (m:Make {name: $make})
        MERGE (cm:CarModel {name: $model, make_name: $make}) ON CREATE SET cm.created_at = timestamp()
        MERGE (cm)-[:BELONGS_TO]->(m)
        CREATE (c:Car {id: $car_id, car_id: $car_id, year: $year, model: $model, make: $make, created_at: datetime()})
        MERGE (c)-[:INSTANCE_OF]->(cm)
        MERGE (c)-[:IS_MAKE]->(m)
        RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make
        """
        return await self._run_single(query, car_id=car_id, year=year, model=model, make=make)

    async def get_car(self, car_id: str):
        return await self._run_single(
            "MATCH (c:Car {id: $car_id})-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make) "
            "RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make LIMIT 1",
            car_id=car_id
        )

    async def list_cars(self, limit: int = 10):
        return await self._run_query(
            "MATCH (c:Car)-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make) "
            "RETURN DISTINCT c {.*} AS car, cm {.*} AS model, m {.*} AS make LIMIT $limit",
            limit=limit
        )

    async def delete_car(self, car_id: str):
        existing = await self._run_single(
            "MATCH (c:Car {id: $car_id}) RETURN c LIMIT 1",
            car_id=car_id
        )
        if not existing:
            return None
        
        result = await self._run_single(
            "MATCH (c:Car {id: $car_id}) DETACH DELETE c RETURN $car_id AS deleted_car_id",
            car_id=car_id
        )
        return {"deleted": True, "car_id": result["deleted_car_id"]} if result else None

    async def update_car(self, car_id: str, update_data: "CarUpdate"):
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_car(car_id)
        
        current = await self.get_car(car_id)
        if not current:
            return None

        params = {"car_id": car_id}
        query_parts = ["MATCH (c:Car {id: $car_id})"]
        
        if "year" in update_dict:
            query_parts.append("SET c.year = $year")
            params["year"] = update_dict["year"]

        if "model" in update_dict or "make" in update_dict:
            new_model = update_dict.get("model", current["model"]["name"])
            new_make = update_dict.get("make", current["make"]["name"])
            
            existing_car = await self._run_single(
                "MATCH (c:Car {make: $new_make, model: $new_model, year: c.year}) "
                "WHERE c.id <> $car_id RETURN c LIMIT 1",
                new_make=new_make, new_model=new_model, car_id=car_id
            )
            if existing_car:
                raise ValueError(f"Car with make '{new_make}', model '{new_model}' already exists with same year")
            
            params.update({"new_model": new_model, "new_make": new_make})
            query_parts.extend([
                "WITH c", "OPTIONAL MATCH (c)-[r:INSTANCE_OF]->() DELETE r", "WITH c",
                "MERGE (make_node:Make {name: $new_make})", 
                "MERGE (model_node:CarModel {name: $new_model, make_name: $new_make})",
                "MERGE (model_node)-[:BELONGS_TO]->(make_node)", 
                "MERGE (c)-[:INSTANCE_OF]->(model_node)",
                "SET c.model = $new_model, c.make = $new_make"
            ])

        query_parts.append(
            "WITH c MATCH (c)-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make) "
            "RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make LIMIT 1"
        )
        return await self._run_single("\n".join(query_parts), **params)

    async def replace_car(self, car_id: str, car_data: "CarCreate"):
        existing = await self._run_single(
            "MATCH (c:Car {make: $make, model: $model, year: $year}) "
            "WHERE c.id <> $car_id RETURN c LIMIT 1",
            make=car_data.make, model=car_data.model, year=car_data.year, car_id=car_id
        )
        if existing:
            raise ValueError(f"Car with make '{car_data.make}', model '{car_data.model}', year {car_data.year} already exists")

        query = """
        MATCH (c:Car {id: $car_id})
        OPTIONAL MATCH (c)-[r:INSTANCE_OF]->() DELETE r
        SET c.year = $year, c.model = $model, c.make = $make
        WITH c
        MERGE (make_node:Make {name: $make})
        MERGE (model_node:CarModel {name: $model, make_name: $make}) ON CREATE SET model_node.created_at = timestamp()
        MERGE (model_node)-[:BELONGS_TO]->(make_node)
        MERGE (c)-[:INSTANCE_OF]->(model_node)
        RETURN c {.*} AS car, model_node {.*} AS model, make_node {.*} AS make
        """
        return await self._run_single(
            query, 
            car_id=car_id, 
            year=car_data.year, 
            model=car_data.model, 
            make=car_data.make
        )
