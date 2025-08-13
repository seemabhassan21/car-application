import logging
from flask import jsonify
from app.extensions import db
from app.models.user import User

logger = logging.getLogger(__name__)

def get_user_by_email(email: str):
    try:
        return db.session.query(User).filter_by(email=email.lower()).first()
    except Exception as e:
        logger.exception(f"Error fetching user by email: {email} — {e}")
        return None


def json_response(payload, status=200):
    return jsonify(payload), status
