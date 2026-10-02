"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables and an optional .env file."""

    app_name: str = "Job Application Tracker API"
    app_version: str = "1.0.0"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://jobtracker:jobtracker@localhost:5432/jobtracker"
    )
    create_tables_on_startup: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for dependency injection."""

    return Settings()


settings = get_settings()
