from sqlalchemy import String, ForeignKey, UniqueConstraint, CheckConstraint, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base


class Make(Base):
    __tablename__ = "makes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    car_models: Mapped[list["CarModel"]] = relationship(
        back_populates="make",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class CarModel(Base):
    __tablename__ = "car_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    make_id: Mapped[int] = mapped_column(ForeignKey("makes.id"), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    make: Mapped["Make"] = relationship(back_populates="car_models", lazy="selectin")
    cars: Mapped[list["Car"]] = relationship(
        back_populates="car_model",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("name", "year", "make_id", name="uq_model_year_make"),
        CheckConstraint("year >= 1990 AND year <= 2026", name="check_year_range"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.make.name if self.make else ''} {self.name} ({self.year})".strip()


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_model_id: Mapped[int] = mapped_column(ForeignKey("car_models.id"), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    car_model: Mapped["CarModel"] = relationship(back_populates="cars", lazy="selectin")

    @property
    def full_name(self) -> str:
        if not self.car_model or not self.car_model.make:
            return ""

        return f"{self.car_model.make.name} {self.car_model.name} ({self.car_model.year})"
