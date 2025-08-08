import logging
from flask_smorest import Blueprint
from flask_jwt_extended import create_access_token

from app.models.user import User
from app.routes.auth.user_schema import UserSchema, LoginSchema
from app.utils.auth import get_user_by_email, commit_instance, json_response

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['POST'])
@auth_bp.arguments(UserSchema)
@auth_bp.response(201, description="User created successfully")
def signup(data):
    if get_user_by_email(data['email']):
        logger.info(f"Signup blocked — email exists: {data['email']}")
        return json_response({"error": "Email already exists"}, 409)

    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'] 
    )

    success, error = commit_instance(user)
    if success:
        logger.info(f"New user created: {data['email']}")
        return json_response({"message": "User created successfully"})
    
    logger.error(f"Signup failed for {data['email']} — {error}")
    return json_response({"error": "Internal server error"}, 500)

@auth_bp.route('/login', methods=['POST'])
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, description="Login successful")
def login(data):
    user = get_user_by_email(data['email'])
    if user and user.check_password(data['password']):
        logger.info(f"User login successful: {data['email']}")
        token = create_access_token(identity=str(user.id))
        return json_response({"access_token": token})
    
    logger.warning(f"Invalid login attempt: {data['email']}")
    return json_response({"error": "Invalid credentials"}, 401)
