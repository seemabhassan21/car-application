from pydantic_settings import BaseSettings 


class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    CAR_API_ID: str
    CAR_MASTER_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
