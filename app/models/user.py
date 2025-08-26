from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.security import security


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = security.hash_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return security.verify_password(raw_password, self.password_hash)
