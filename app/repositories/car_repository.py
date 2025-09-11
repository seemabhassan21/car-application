from neo4j import AsyncSession
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.cars.car_schema import CarUpdate, CarCreate


class CarRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_make(self, name: str):
        query = """
        MERGE (m:Make {name: $name})
        RETURN m {.*} AS make
        """
        result = await self.session.run(query, name=name)  # type: ignore[arg-type]
        record = await result.single()
        return dict(record["make"]) if record else None

    async def create_model(self, model_name: str, make_name: str):
        query = """
        MATCH (m:Make {name: $make_name})
        MERGE (cm:CarModel {name: $model_name})
        MERGE (cm)-[:BELONGS_TO]->(m)
        RETURN cm {.*} AS model, m {.*} AS make
        """
        result = await self.session.run(  # type: ignore[arg-type]
            query, model_name=model_name, make_name=make_name
        )
        record = await result.single()
        if record:
            return {"model": dict(record["model"]), "make": dict(record["make"])}
        return None

    async def create_car(self, car_id: str, year: int, model_name: str, make_name: str):
        query = """
        MATCH (cm:CarModel {name: $model_name})-[:BELONGS_TO]->(m:Make {name: $make_name})
        CREATE (c:Car {id: $car_id, year: $year})
        MERGE (c)-[:INSTANCE_OF]->(cm)
        RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make
        """
        result = await self.session.run(  # type: ignore[arg-type]
            query,
            car_id=car_id,
            year=year,
            model_name=model_name,
            make_name=make_name,
        )
        record = await result.single()
        if record:
            return {
                "car": dict(record["car"]),
                "model": dict(record["model"]),
                "make": dict(record["make"]),
            }
        return None

    async def get_car(self, car_id: str):
        query = """
        MATCH (c:Car {id: $car_id})-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make)
        RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make
        """
        result = await self.session.run(query, car_id=car_id)  # type: ignore[arg-type]
        record = await result.single()
        if record:
            return {
                "car": dict(record["car"]),
                "model": dict(record["model"]),
                "make": dict(record["make"]),
            }
        return None

    async def list_cars(self, limit: int = 10):
        query = """
        MATCH (c:Car)-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make)
        RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make
        LIMIT $limit
        """
        result = await self.session.run(query, limit=limit)  # type: ignore[arg-type]
        records = [r async for r in result]
        return [
            {
                "car": dict(r["car"]),
                "model": dict(r["model"]),
                "make": dict(r["make"]),
            }
            for r in records
        ]

    async def update_car(self, car_id: str, update_data: "CarUpdate"):
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_car(car_id)

        query_parts = ["MATCH (c:Car {id: $car_id})"]
        params = {"car_id": car_id}

        if "year" in update_dict:
            query_parts.append("SET c.year = $year")
            params["year"] = update_dict["year"]

        if "model_name" in update_dict or "make_name" in update_dict:
            current_car_data = await self.get_car(car_id)
            if not current_car_data:
                return None
            new_model_name = update_dict.get(
                "model_name", current_car_data["model"]["name"]
            )
            new_make_name = update_dict.get(
                "make_name", current_car_data["make"]["name"]
            )
            params["new_model_name"] = new_model_name
            params["new_make_name"] = new_make_name
            query_parts.extend(
                [
                    "WITH c",
                    "MATCH (c)-[r:INSTANCE_OF]->()",
                    "DELETE r",
                    "WITH c",
                    "MATCH (new_model:CarModel {name: $new_model_name})"
                    "-[:BELONGS_TO]->(new_make:Make {name: $new_make_name})",
                    "MERGE (c)-[:INSTANCE_OF]->(new_model)",
                ]
            )

        query_parts.append(
            "WITH c "
            "MATCH (c)-[:INSTANCE_OF]->(cm:CarModel)-[:BELONGS_TO]->(m:Make) "
            "RETURN c {.*} AS car, cm {.*} AS model, m {.*} AS make"
        )
        query = "\n".join(query_parts)

        result = await self.session.run(query, params)  # type: ignore[arg-type]
        record = await result.single()
        if record:
            return {
                "car": dict(record["car"]),
                "model": dict(record["model"]),
                "make": dict(record["make"]),
            }
        return None

    async def replace_car(self, car_id: str, car_data: "CarCreate"):
        query = """
        MATCH (c:Car {id: $car_id})
        OPTIONAL MATCH (c)-[r:INSTANCE_OF]->()
        DELETE r
        WITH c
        SET c.year = $year
        WITH c
        MATCH (new_model:CarModel {name: $model_name})-[:BELONGS_TO]->(new_make:Make {name: $make_name})
        MERGE (c)-[:INSTANCE_OF]->(new_model)
        RETURN c {.*} AS car, new_model {.*} AS model, new_make {.*} AS make
        """
        params = {
            "car_id": car_id,
            "year": car_data.year,
            "model_name": car_data.model_name,
            "make_name": car_data.make_name,
        }
        result = await self.session.run(query, params)  # type: ignore[arg-type]
        record = await result.single()
        if record:
            return {
                "car": dict(record["car"]),
                "model": dict(record["model"]),
                "make": dict(record["make"]),
            }
        return None

    async def delete_car(self, car_id: str):
        query = """
        MATCH (c:Car {id: $car_id})
        DETACH DELETE c
        RETURN $car_id AS car_id
        """
        result = await self.session.run(query, car_id=car_id)  # type: ignore[arg-type]
        record = await result.single()
        return {"deleted": True, "car_id": record["car_id"]} if record else None
