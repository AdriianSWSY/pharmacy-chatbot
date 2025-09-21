"""
Staging environment configuration.
"""

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from config.base import BaseConfig, ServerConfig, PharmacyAPIConfig, CacheConfig


class StagingConfig(BaseConfig):
    """Staging environment configuration."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.staging"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
    )

    debug: bool = Field(default=False)
    environment: str = Field(default="staging")

    # Override with staging-specific settings
    server: ServerConfig = Field(
        default_factory=lambda: ServerConfig(
            host="0.0.0.0", port=8000, log_level="info"
        )
    )

    pharmacy_api: PharmacyAPIConfig = Field(
        default_factory=lambda: PharmacyAPIConfig(
            base_url="https://api.staging.example.com",  # Staging API URL
            timeout=45,  # Longer timeout for staging
            retry_count=5,  # More retries for staging
            retry_delay=2.0,
        )
    )

    cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(
            ttl=1800  # 30 minutes for staging
        )
    )
