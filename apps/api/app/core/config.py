from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Hermes Forecast API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg2://volaris:volaris_dev_pw@localhost:5432/volaris"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    cors_origins: list[str] = ["http://localhost:3000"]

    market_data_provider: str = "mock"
    polygon_api_key: str | None = None
    alpha_vantage_api_key: str | None = None

    rate_limit_backend: str = "memory"
    rate_limit_requests_per_window: int = 120
    rate_limit_window_seconds: int = 60

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None
    google_oauth_redirect_uri: str = "http://localhost:3000/auth/callback/google"


@lru_cache
def get_settings() -> Settings:
    return Settings()
