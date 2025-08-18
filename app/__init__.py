from flask import Flask
from flask_smorest import Api

from app.config import Config
from app.extensions import db, jwt, ma, migrate
from app.routes import all_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)
    ma.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # Ensure models are loaded before migrations

    api = Api(app)
    for bp, prefix in all_blueprints:
        api.register_blueprint(bp, url_prefix=prefix)

    return app
