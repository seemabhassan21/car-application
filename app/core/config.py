from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    jwt_secret_key: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7

    ASYNC_DATABASE_URL: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    default_page: int = 1
    default_per_page: int = 10
    max_per_page: int = 100

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
