import logging
from flask import request
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from app.routes.cars.car_schema import CarSchema, CarUpdateSchema
from app.utils.cars import (
    create_car, get_all_cars, get_car_by_id,
    update_car, delete_car
)
from app.utils.auth import json_response

car_bp = Blueprint("cars", __name__, url_prefix="/api/cars")
logger = logging.getLogger(__name__)

@car_bp.route("/", methods=["POST"])
@car_bp.arguments(CarSchema)
@jwt_required()
def create_car_route(data):
    car, error = create_car(**data)
    if error:
        return json_response({"error": error}, 500)
    return json_response(CarSchema().dump(car), 201)

@car_bp.route("/", methods=["GET"])
@jwt_required()
def list_cars():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    result = get_all_cars(page=page, per_page=per_page)
    return json_response({
        "items": CarSchema(many=True).dump(result["items"]),
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"]
    })

@car_bp.route("/<int:car_id>", methods=["GET"])
@jwt_required()
def get_car_route(car_id):
    car = get_car_by_id(car_id)
    if not car:
        return json_response({"error": "Car not found"}, 404)
    return json_response(CarSchema().dump(car))

@car_bp.route("/<int:car_id>", methods=["PATCH"])
@car_bp.arguments(CarUpdateSchema)
@jwt_required()
def update_car_route(data, car_id):
    car, error = update_car(car_id, **data)
    if error:
        code = 404 if "not found" in error.lower() else 500
        return json_response({"error": error}, code)
    return json_response(CarSchema().dump(car))

@car_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def delete_car_route(car_id):
    success, error = delete_car(car_id)
    if not success:
        code = 404 if "not found" in error.lower() else 500
        return json_response({"error": error}, code)
    return json_response({"message": "Car deleted"})
