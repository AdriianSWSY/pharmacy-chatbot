"""
Production environment configuration.
"""

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from config.base import BaseConfig, ServerConfig, PharmacyAPIConfig, CacheConfig


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.production"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
    )

    debug: bool = Field(default=False)
    environment: str = Field(default="production")

    # Override with production-specific settings
    server: ServerConfig = Field(
        default_factory=lambda: ServerConfig(
            host="0.0.0.0",
            port=8000,
            log_level="warning",  # Less verbose logging in production
        )
    )

    pharmacy_api: PharmacyAPIConfig = Field(
        default_factory=lambda: PharmacyAPIConfig(
            base_url="https://api.example.com",  # Production API URL
            timeout=60,  # Longer timeout for production stability
            retry_count=5,  # More retries for production
            retry_delay=3.0,  # Longer delay between retries
        )
    )

    cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(
            ttl=3600  # 1 hour cache for production
        )
    )
