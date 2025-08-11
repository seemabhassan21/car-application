from marshmallow import Schema, fields, validate, EXCLUDE
from datetime import datetime

NAME_VALIDATOR = validate.Length(min=5, max=100)
YEAR_VALIDATOR = validate.Range(min=2000, max=datetime.now().year + 1)


class MakeInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, validate=NAME_VALIDATOR)


class MakeOutputSchema(Schema):
    """Output schema for Make"""
    class Meta:
        unknown = EXCLUDE

    id = fields.Int()
    name = fields.Str()



class CarModelInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, validate=NAME_VALIDATOR)
    year = fields.Int(required=True, validate=YEAR_VALIDATOR)
    make_id = fields.Int(required=True)


class CarModelOutputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int()
    name = fields.Str()
    year = fields.Int()
    make = fields.Nested(MakeOutputSchema)


class CarInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    car_model_id = fields.Int(required=True)


class CarOutputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int()
    car_model_info = fields.Nested(CarModelOutputSchema)
    created_at = fields.DateTime()
    full_name = fields.Str()
    make = fields.Str()
    model = fields.Str()
    year = fields.Int()


class CarUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    car_model_id = fields.Int(required=False)
