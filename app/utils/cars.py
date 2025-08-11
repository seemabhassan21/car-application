import logging
from sqlalchemy import select, func
from app import db
from app.models import CarModel

logger = logging.getLogger(__name__)

def create_car(make, model, year):
    car = CarModel(make=make, model=model, year=year)
    try:
        db.session.add(car)
        db.session.commit()
        logger.info(f"Car created: {make} {model} {year}")
        return car, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating car: {e}")
        return None, str(e)


def get_all_cars(page=1, per_page=10):
    stmt = select(CarModel).offset((page - 1) * per_page).limit(per_page)
    cars = db.session.execute(stmt).scalars().all()

    total = db.session.execute(select(func.count(CarModel.id))).scalar()

    return {
        "items": cars,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page  # ceil division
    }


def get_car_by_id(car_id):
    stmt = select(CarModel).where(CarModel.id == car_id)
    return db.session.execute(stmt).scalar_one_or_none()


def get_car_by_details(make, model, year):
    stmt = select(CarModel).where(
        CarModel.make == make,
        CarModel.model == model,
        CarModel.year == year
    )
    return db.session.execute(stmt).scalar_one_or_none()


def update_car(car_id, make=None, model=None, year=None):
    car = get_car_by_id(car_id)
    if not car:
        return None, "Car not found"
    
    if make is not None:
        car.make = make
    if model is not None:
        car.model = model
    if year is not None:
        car.year = year

    try:
        db.session.commit()
        logger.info(f"Car updated: {car_id}")
        return car, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating car {car_id}: {e}")
        return None, str(e)


def delete_car(car_id):
    car = get_car_by_id(car_id)
    if not car:
        return False, "Car not found"
    try:
        db.session.delete(car)
        db.session.commit()
        logger.info(f"Car deleted: {car_id}")
        return True, None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting car {car_id}: {e}")
        return False, str(e)
