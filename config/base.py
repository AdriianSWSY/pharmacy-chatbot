"""
Base configuration module for the AI Agent Call Assistant.
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    """Server configuration settings."""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    log_level: str = Field(default="info", description="Logging level")


class PharmacyAPIConfig(BaseModel):
    """External pharmacy API configuration."""

    base_url: str = Field(description="Base URL for pharmacy API")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries")
    retry_delay: float = Field(
        default=1.0, description="Initial retry delay in seconds"
    )


class CacheConfig(BaseModel):
    """Cache configuration settings."""

    ttl: int = Field(default=3600, description="Cache TTL in seconds (1 hour)")


class AgentSettings(BaseModel):
    """LangChain agent configuration."""

    model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=500, description="Max tokens per response")
    memory_type: str = Field(default="buffer", description="Memory type")
    session_timeout: int = Field(default=1800, description="Session timeout in seconds")


class BaseConfig(BaseSettings):
    """Base configuration class using pydantic-settings for environment variable loading."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(
        default="AI Agent Call Assistant API", description="Application name"
    )
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Component configurations
    server: ServerConfig = Field(default_factory=lambda: ServerConfig())
    pharmacy_api: PharmacyAPIConfig = Field(
        default_factory=lambda: PharmacyAPIConfig(base_url="https://api.example.com")
    )
    cache: CacheConfig = Field(default_factory=lambda: CacheConfig())
    agent: AgentSettings = Field(default_factory=lambda: AgentSettings())
