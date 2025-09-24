"""
Agent factory for creating appropriate agents based on phone number lookup.
"""

from typing import Optional, Union, TYPE_CHECKING
import logging
from src.utils.phone import normalize_phone
from src.services.pharmacy_service import PharmacyService
from src.models.pharmacy import Pharmacy

if TYPE_CHECKING:
    from src.agents.info_agent import InfoAgent
    from src.agents.collection_agent import CollectionAgent

logger = logging.getLogger(__name__)


class AgentFactory:
    """Creates appropriate agent based on phone number lookup."""

    def __init__(self, pharmacy_service: PharmacyService):
        """
        Initialize the agent factory.

        Args:
            pharmacy_service: Pharmacy service instance for lookups
        """
        self.pharmacy_service = pharmacy_service

    async def create_agent(
        self, phone: str, session_id: str
    ) -> Union["InfoAgent", "CollectionAgent"]:
        """
        Create appropriate agent based on phone number lookup.

        Args:
            phone: Phone number to lookup
            session_id: Unique session identifier

        Returns:
            InfoAgent if pharmacy found, CollectionAgent if not found

        Raises:
            ValueError: If phone number is invalid
        """
        # Validate phone number
        if not self._validate_phone(phone):
            raise ValueError(f"Invalid phone number format: {phone}")

        # Lookup pharmacy
        pharmacy = await self._lookup_pharmacy(phone)

        # Create appropriate agent
        if pharmacy:
            logger.info(f"Creating InfoAgent for existing pharmacy: {pharmacy.name}")
            from src.agents.info_agent import InfoAgent

            return InfoAgent(session_id=session_id, pharmacy=pharmacy)
        else:
            logger.info(
                f"Creating CollectionAgent for new pharmacy with phone: {phone}"
            )
            from src.agents.collection_agent import CollectionAgent

            return CollectionAgent(session_id=session_id, phone=phone)

    def _validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        normalized = normalize_phone(phone)
        return normalized is not None

    async def _lookup_pharmacy(self, phone: str) -> Optional[Pharmacy]:
        """
        Lookup pharmacy by phone number.

        Args:
            phone: Phone number to lookup

        Returns:
            Pharmacy if found, None otherwise
        """
        try:
            pharmacy = await self.pharmacy_service.search_by_phone(phone)
            if pharmacy:
                logger.info(f"Found pharmacy: {pharmacy.name} for phone: {phone}")
            else:
                logger.info(f"No pharmacy found for phone: {phone}")
            return pharmacy
        except Exception as e:
            logger.error(f"Error looking up pharmacy for phone {phone}: {e}")
            return None
