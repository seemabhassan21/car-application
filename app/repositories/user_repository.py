import uuid
from typing import Any
from typing_extensions import LiteralString
from neo4j import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _fetch_one(self, query: LiteralString | str, **params) -> dict[str, Any] | None:
        result = await self.session.run(query, **params)
        record = await result.single()
        return dict(record["user"]) if record else None

    async def create_user(self, username: str, email: str, password_hash: str) -> dict[str, Any] | None:
        return await self._fetch_one(
            """
            CREATE (u:User {id: $id, username: $username, email: $email, password_hash: $password_hash})
            RETURN u {.*} AS user
            """,
            id=str(uuid.uuid4()), username=username, email=email, password_hash=password_hash
        )

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        return await self._fetch_one(
            "MATCH (u:User {username: $username}) RETURN u {.*} AS user", username=username
        )

    async def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        return await self._fetch_one(
            "MATCH (u:User {id: $user_id}) RETURN u {.*} AS user", user_id=user_id
        )

    @staticmethod
    def to_public_dict(user: dict[str, Any] | None) -> dict[str, Any] | None:
        return {k: user[k] for k in ("id", "username", "email")} if user else None
