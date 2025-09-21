"""
Development environment configuration.
"""

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from config.base import BaseConfig, ServerConfig, PharmacyAPIConfig, CacheConfig


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.development"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
    )

    debug: bool = Field(default=True)
    environment: str = Field(default="development")

    # Override with development-specific settings
    server: ServerConfig = Field(
        default_factory=lambda: ServerConfig(
            host="0.0.0.0", port=8000, log_level="debug"
        )
    )

    pharmacy_api: PharmacyAPIConfig = Field(
        default_factory=lambda: PharmacyAPIConfig(
            base_url="https://api.dev.example.com"
        )
    )

    cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(
            ttl=300  # 5 minutes for faster development testing
        )
    )
