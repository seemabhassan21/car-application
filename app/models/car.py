from datetime import datetime, timezone

from sqlalchemy.sql import func

from app.extensions import db


class Make(db.Model):
    __tablename__ = 'makes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    car_models = db.relationship(
        'CarModel',
        back_populates='make',
        lazy='selectin',
        cascade='all, delete-orphan'
    )


class CarModel(db.Model):
    __tablename__ = 'car_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    make_id = db.Column(
        db.Integer,
        db.ForeignKey('makes.id'),
        nullable=False,
        index=True
    )

    make = db.relationship('Make', back_populates='car_models', lazy='selectin')
    cars = db.relationship(
        'Car',
        back_populates='car_model',
        lazy='selectin',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('name', 'year', 'make_id', name='uq_model_year_make'),
        db.CheckConstraint('year >= 2000 AND year <= 2026', name='check_year_range'),
    )

    @property
    def full_name(self):
        return f"{self.make.name} {self.name} ({self.year})"


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    car_model_id = db.Column(
        db.Integer,
        db.ForeignKey('car_models.id'),
        nullable=False,
        index=True
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    car_model = db.relationship('CarModel', back_populates='cars', lazy='selectin')

    @property
    def full_name(self):
        return f"{self.car_model.make.name} {self.car_model.name} ({self.car_model.year})"

    @property
    def make_name(self):
        return self.car_model.make.name

    @property
    def model_name(self):
        return self.car_model.name

    @property
    def year(self):
        return self.car_model.year
