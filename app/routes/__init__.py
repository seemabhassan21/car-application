from app.routes.auth.auth_routes import auth_bp
from app.routes.cars.car_routes import car_bp

all_blueprints = [
    (auth_bp, '/api/auth'),
    (car_bp, '/api/cars'),
]
