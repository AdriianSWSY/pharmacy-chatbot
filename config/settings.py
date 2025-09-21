"""
Configuration settings manager for the AI Agent Call Assistant.
"""

import os
from functools import lru_cache
from config.base import BaseConfig
from config.development import DevelopmentConfig
from config.staging import StagingConfig
from config.production import ProductionConfig


class ConfigFactory:
    """Factory for creating appropriate configuration instances."""

    _configs = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "staging": StagingConfig,
        "stage": StagingConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
    }

    @classmethod
    def get_config(cls, env: str = None) -> BaseConfig:
        """
        Get configuration instance for the specified environment.

        Args:
            env: Environment name. If None, reads from ENVIRONMENT env var

        Returns:
            Configuration instance for the environment

        Raises:
            ValueError: If environment is not supported
        """
        if env is None:
            env = os.getenv("ENVIRONMENT", "development")

        env = env.lower()

        if env not in cls._configs:
            available = ", ".join(cls._configs.keys())
            raise ValueError(f"Unsupported environment '{env}'. Available: {available}")

        config_class = cls._configs[env]

        # Create instance - pydantic-settings handles environment loading automatically
        return config_class()

    @classmethod
    def list_environments(cls) -> list:
        """Get list of supported environments."""
        return list(cls._configs.keys())


@lru_cache
def get_settings() -> BaseConfig:
    """
    Get the current configuration settings (cached).

    Returns:
        Current configuration instance
    """
    return ConfigFactory.get_config()


# Create global config instance (for backwards compatibility)
settings = get_settings()
