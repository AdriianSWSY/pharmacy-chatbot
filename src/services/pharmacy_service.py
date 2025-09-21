"""
Service layer for pharmacy operations with caching and search functionality.
"""

from typing import List, Optional
import logging
from src.models.pharmacy import Pharmacy
from src.clients.pharmacy_api import PharmacyAPIClient
from src.utils.phone import normalize_phone

logger = logging.getLogger(__name__)


class PharmacyService:
    """Manages pharmacy data with search capabilities."""

    def __init__(self, api_client: PharmacyAPIClient):
        """
        Initialize the pharmacy service.

        Args:
            api_client: Pharmacy API client instance
        """
        self.api_client = api_client
        self._normalize_phone = normalize_phone

    async def get_all_pharmacies(self) -> List[Pharmacy]:
        """
        Get all pharmacies.

        Returns:
            List of all pharmacy objects
        """
        # Fetch data from API
        logger.info("Fetching pharmacy data from API")
        try:
            pharmacies = await self.api_client.fetch_pharmacies()
            logger.info(f"Fetched {len(pharmacies)} pharmacies")
            return pharmacies

        except Exception as e:
            logger.error(f"Failed to fetch pharmacies: {e}")
            raise

    async def search_by_phone(self, phone: str) -> Optional[Pharmacy]:
        """
        Search for a pharmacy by phone number.

        Args:
            phone: Phone number to search for

        Returns:
            Pharmacy object if found, None otherwise
        """
        if not phone:
            logger.warning("Empty phone number provided for search")
            return None

        normalized_search = self._normalize_phone(phone)

        if not normalized_search:
            logger.warning(f"Invalid phone number format: {phone}")
            return None

        pharmacies = await self.get_all_pharmacies()

        # Search for matching phone number
        for pharmacy in pharmacies:
            normalized_pharmacy_phone = self._normalize_phone(pharmacy.phone)

            if normalized_pharmacy_phone == normalized_search:
                logger.info(f"Found pharmacy match for phone {phone}: {pharmacy.name}")
                return pharmacy

        logger.info(f"No pharmacy found for phone {phone}")
        return None
