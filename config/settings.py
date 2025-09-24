"""
Configuration settings manager for the AI Agent Call Assistant.

Simple environment-based configuration using pydantic-settings.
"""

import os
from functools import lru_cache
from config.base import BaseConfig


@lru_cache
def get_settings() -> BaseConfig:
    """
    Get configuration based on environment.

    The configuration is loaded from:
    1. Environment variables
    2. .env file (base configuration)
    3. .env.{environment} file (environment-specific overrides)

    Returns:
        Configuration instance for the current environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    # Create config with appropriate env files
    # Pydantic-settings will handle all the loading and merging
    return BaseConfig(_env_file=[".env", f".env.{env}"], environment=env)


# Create global settings instance
settings = get_settings()
