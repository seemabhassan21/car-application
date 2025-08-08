from marshmallow import Schema, fields, validate, EXCLUDE

from datetime import datetime

NAME_VALIDATOR = validate.Length(min=5, max=100)
YEAR_VALIDATOR = validate.Range(min=2000, max=datetime.now().year + 1)


class MakeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=NAME_VALIDATOR)


class CarModelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=NAME_VALIDATOR)
    year = fields.Int(required=True, validate=YEAR_VALIDATOR)
    make_id = fields.Int(required=True, load_only=True)
    make = fields.Nested(MakeSchema, dump_only=True)


class CarSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    car_model_id = fields.Int(load_only=True)

    car_model_info = fields.Nested(CarModelSchema, dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    full_name = fields.Str(dump_only=True)

    make = fields.Str(load_only=True, validate=NAME_VALIDATOR)
    model = fields.Str(load_only=True, validate=NAME_VALIDATOR)
    year = fields.Int(load_only=True, validate=YEAR_VALIDATOR)


class CarUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    make = fields.Str(validate=NAME_VALIDATOR, required=False)
    model = fields.Str(validate=NAME_VALIDATOR, required=False)
    year = fields.Int(validate=YEAR_VALIDATOR, required=False)
