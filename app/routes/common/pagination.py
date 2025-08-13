from marshmallow import Schema, fields, EXCLUDE, validate
from typing import Type

class PaginationInputSchema(Schema):
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1),
        metadata={"description": "Page number (1-based)"}
    )
    per_page = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100),
        metadata={"description": "Number of items per page (1-100)"}
    )


class PaginationMetaSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = fields.Int(required=True)
    per_page = fields.Int(required=True)
    total = fields.Int(required=True, metadata={"description": "Total items"})
    pages = fields.Int(required=True, metadata={"description": "Total pages"})


class PaginatedResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(fields.Raw(), required=True)
    meta = fields.Nested(PaginationMetaSchema, required=True)


def make_paginated_schema(item_schema_cls: Type[Schema]) -> Type[Schema]:
  
    class _TypedPaginatedSchema(PaginatedResponseSchema):
        items = fields.List(fields.Nested(item_schema_cls), required=True)

    _TypedPaginatedSchema.__name__ = f"Paginated{item_schema_cls.__name__}List"
    return _TypedPaginatedSchema
