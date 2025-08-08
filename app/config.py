import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(var_name, required=True, default=None):
    value = os.getenv(var_name)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")
    return value or default

class Config:
   
    API_TITLE = "Carbase API"         
    API_VERSION = "v1"                
    OPENAPI_VERSION = "3.0.2"       

    OPENAPI_URL_PREFIX = "/api"  
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    
    SECRET_KEY = get_env_var("SECRET_KEY")
    JWT_SECRET_KEY = get_env_var("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = get_env_var("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = get_env_var("CELERY_BROKER_URL", default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = get_env_var("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
    CAR_API_URL = "https://parseapi.back4app.com/classes/Car_Model_List?limit=10000"
    CAR_API_HEADERS = {
        'X-Parse-Application-Id': get_env_var("CAR_API_ID"),
        'X-Parse-Master-Key': get_env_var("CAR_API_KEY")
    }
    