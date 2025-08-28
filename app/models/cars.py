from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base
import random


class Make(Base):
    __tablename__ = "makes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    car_models: Mapped[list["CarModel"]] = relationship("CarModel", back_populates="make")


class CarModel(Base):
    __tablename__ = "car_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    make_id: Mapped[int] = mapped_column(ForeignKey("makes.id"), nullable=False)

    make: Mapped["Make"] = relationship("Make", back_populates="car_models")
    cars: Mapped[list["Car"]] = relationship("Car", back_populates="car_model")

    __table_args__ = (
        UniqueConstraint("make_id", "name", "year", name="uq_car_model_make_name_year"),
    )


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_model_id: Mapped[int] = mapped_column(ForeignKey("car_models.id"), nullable=False)
    vin: Mapped[str] = mapped_column(String(12), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    car_model: Mapped["CarModel"] = relationship("CarModel", back_populates="cars")

    __table_args__ = (
        UniqueConstraint("vin", name="uq_car_vin"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.car_model.make.name} {self.car_model.name} ({self.car_model.year})"

    @staticmethod
    def generate_vin(model_name: str, year: int) -> str:
        prefix = ''.join(c for c in model_name.upper() if c.isalnum())[:3] or "CAR"
        year_suffix = str(year)[-2:] if year else "00"
        random_digits = ''.join(random.choices('0123456789', k=3))
        return f"{prefix}{year_suffix}-{random_digits}"
