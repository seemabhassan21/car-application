from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from app.extensions import db
from app.models.car import Car
from app.routes.cars.car_schema import CarInputSchema, CarUpdateSchema, CarOutputSchema
from app.routes.common.pagination import PaginationInputSchema, make_paginated_schema
from app.utils.db_helper import get_or_404, paginate_query, commit_or_500
from app.utils.auth import json_response

car_bp = Blueprint("cars", __name__)

CarListResponseSchema = make_paginated_schema(CarOutputSchema)


@car_bp.route("/", methods=["POST"])
@car_bp.arguments(CarInputSchema)
@car_bp.response(201, CarOutputSchema)
@jwt_required()
def create_car(data):
    car = Car(**data)
    return commit_or_500(car, db.session)


@car_bp.route("/", methods=["GET"])
@car_bp.arguments(PaginationInputSchema, location="query")
@car_bp.response(200, CarListResponseSchema)
@jwt_required()
def list_cars(pagination):
    query = select(Car)
    return paginate_query(query, pagination["page"], pagination["per_page"])


@car_bp.route("/<int:car_id>", methods=["GET"])
@car_bp.response(200, CarOutputSchema)
@jwt_required()
def get_car(car_id):
    return get_or_404(Car, car_id)


@car_bp.route("/<int:car_id>", methods=["PATCH"])
@car_bp.arguments(CarUpdateSchema)
@car_bp.response(200, CarOutputSchema)
@jwt_required()
def update_car_partial(data, car_id):
    car = get_or_404(Car, car_id)
    validated_data = CarUpdateSchema(partial=True).load(data)
    db.session.query(Car).filter(Car.id == car_id).update(validated_data, synchronize_session="fetch")
    return commit_or_500(db.session.get(Car, car_id), db.session)


@car_bp.route("/<int:car_id>", methods=["PUT"])
@car_bp.arguments(CarInputSchema)
@car_bp.response(200, CarOutputSchema)
@jwt_required()
def replace_car(data, car_id):
    car = get_or_404(Car, car_id)
    validated_data = CarInputSchema().load(data)
    db.session.query(Car).filter(Car.id == car_id).update(validated_data, synchronize_session="fetch")
    return commit_or_500(db.session.get(Car, car_id), db.session)


@car_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id):
    car = get_or_404(Car, car_id)
    db.session.delete(car)
    return commit_or_500(car, db.session)
