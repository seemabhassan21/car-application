import logging
from flask import jsonify
from app.extensions import db
from app.models.user import User

logger = logging.getLogger(__name__)


def get_user_by_email(email: str, session=None):
    sess = session or db.session
    try:
        return sess.query(User).filter_by(email=email.lower()).first()
    except Exception:
        logger.exception("Error fetching user by email: %s", email)
        return None


def json_response(payload, status=200):
    return jsonify(payload), status
