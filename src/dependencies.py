"""
Simple dependency injection for FastAPI endpoints.
"""

from functools import lru_cache
from src.services.pharmacy_service import PharmacyService
from src.clients.pharmacy_api import PharmacyAPIClient
from config.settings import get_settings


@lru_cache
def get_pharmacy_service() -> PharmacyService:
    """
    Get pharmacy service instance.

    Returns:
        PharmacyService instance with configured API client
    """
    settings = get_settings()

    # Create API client
    api_client = PharmacyAPIClient(
        base_url=settings.pharmacy_api.base_url,
        timeout=settings.pharmacy_api.timeout,
        retry_count=settings.pharmacy_api.retry_count,
        retry_delay=settings.pharmacy_api.retry_delay,
    )

    # Create and return service
    return PharmacyService(api_client=api_client)
