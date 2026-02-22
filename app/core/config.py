"""Application configuration module."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "AI Translation Studio"
    app_env: str = "development"
    default_source_language: str = "en"
    default_target_language: str = "es"
    request_timeout_seconds: float = 10.0
    libretranslate_url: str = "https://libretranslate.com/translate"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
