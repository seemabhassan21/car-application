from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column('password_hash', db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def password(self):
        raise AttributeError("Password is write-only use `check_password()` to verify.")

    @password.setter
    def password(self, raw_password):
        self._password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self._password_hash, raw_password)
