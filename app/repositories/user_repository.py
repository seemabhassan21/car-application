import uuid
from typing import Any
from neo4j import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self, username: str, email: str, password_hash: str
    ) -> dict[str, Any] | None:
        user_id = str(uuid.uuid4())
        query = """
        CREATE (u:User {id: $id, username: $username, email: $email, password_hash: $password_hash})
        RETURN u {.*} AS user
        """
        result = await self.session.run(
            query,
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
        )
        record = await result.single()
        return dict(record["user"]) if record else None

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        query = """
        MATCH (u:User {username: $username})
        RETURN u {.*} AS user
        """
        result = await self.session.run(query, username=username)
        record = await result.single()
        return dict(record["user"]) if record else None

    @staticmethod
    def to_public_dict(user: dict[str, Any] | None) -> dict[str, Any] | None:
        """Strip sensitive fields (like password_hash) for safe API responses."""
        if not user:
            return None
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        }
