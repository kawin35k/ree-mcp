"""Application settings using pydantic-settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        ree_api_token: REE API authentication token
        ree_api_base_url: Base URL for REE API
        request_timeout: HTTP request timeout in seconds
        max_retries: Maximum number of retry attempts for failed requests
        retry_backoff_factor: Backoff factor for exponential retry
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ree_api_token: str = Field(
        ...,
        description="REE API authentication token",
    )
    ree_api_base_url: str = Field(
        default="https://api.esios.ree.es",
        description="Base URL for REE API",
    )
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
        ge=1,
        le=300,
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts",
        ge=0,
        le=10,
    )
    retry_backoff_factor: float = Field(
        default=0.5,
        description="Exponential backoff factor",
        ge=0.0,
        le=10.0,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Singleton Settings instance.
    """
    return Settings()  # type: ignore[call-arg]
