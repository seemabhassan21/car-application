from typing import Generic, List, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")


class CursorPage(GenericModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[int] = None
    limit: int


async def cursor_paginate(
    query,
    session,
    model_id_field: str = "id",
    limit: int = 10,
    cursor: Optional[int] = None,
) -> CursorPage:
    if cursor:
        entity = query.column_descriptions[0]["entity"]
        id_field = getattr(entity, model_id_field)
        query = query.where(id_field > cursor)

    entity = query.column_descriptions[0]["entity"]
    id_field = getattr(entity, model_id_field)
    query = query.order_by(id_field).limit(limit)

    result = await session.execute(query)
    items = result.scalars().all()

    next_cursor = getattr(items[-1], model_id_field) if items else None

    return CursorPage(items=items, next_cursor=next_cursor, limit=limit)
