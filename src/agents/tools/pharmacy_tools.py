"""
LangChain tools for querying pharmacy information.
"""

from typing import List, Optional
from langchain_core.tools import Tool
from src.models.pharmacy import Pharmacy
import logging

logger = logging.getLogger(__name__)


class PharmacyTools:
    """Tools for querying pharmacy information."""

    def __init__(self, pharmacy: Pharmacy):
        """
        Initialize pharmacy tools.

        Args:
            pharmacy: Pharmacy instance to query
        """
        self.pharmacy: Pharmacy = pharmacy

    def get_prescriptions(self, input: Optional[str] = None) -> str:
        """
        Retrieves prescription data for the pharmacy.

        Args:
            input: Optional input (not used, but required for LangChain tools)

        Returns:
            Formatted string of prescriptions
        """
        if not self.pharmacy.prescriptions:
            return "No prescriptions found for this pharmacy."

        prescriptions = []
        for idx, prescription in enumerate(self.pharmacy.prescriptions, 1):
            prescriptions.append(
                f"{idx}. {prescription.drug} - Quantity: {prescription.count}, "
            )

        return "\n".join(prescriptions)

    def get_pharmacy_details(self, field: str) -> str:
        """
        Gets specific pharmacy field information.

        Args:
            field: The field to retrieve (name, phone, email, city, state)

        Returns:
            The requested field value or error message
        """
        field = field.lower().strip()

        field_map = {
            "name": self.pharmacy.name,
            "phone": self.pharmacy.phone,
            "email": self.pharmacy.email,
            "city": self.pharmacy.city,
            "state": self.pharmacy.state,
            "id": str(self.pharmacy.id),
        }

        if field in field_map:
            return field_map[field]

        if field == "prescriptions":
            return self.get_prescriptions()

        available_fields = ", ".join(field_map.keys())
        return f"Invalid field '{field}'. Available fields: {available_fields}, prescriptions"

    def get_pharmacy_summary(self, input: Optional[str] = None) -> str:
        """
        Get a complete summary of the pharmacy.

        Args:
            input: Optional input (not used, but required for LangChain tools)

        Returns:
            Formatted summary of all pharmacy information
        """
        summary = [
            f"Pharmacy: {self.pharmacy.name}",
            f"Phone: {self.pharmacy.phone}",
            f"Email: {self.pharmacy.email}",
            f"Location: {self.pharmacy.city}, {self.pharmacy.state}",
        ]

        if self.pharmacy.prescriptions:
            summary.append(f"Total Prescriptions: {len(self.pharmacy.prescriptions)}")

        return "\n".join(summary)


def create_pharmacy_tools(pharmacy: Pharmacy) -> List[Tool]:
    """
    Create a list of pharmacy tools for an agent.

    Args:
        pharmacy: Pharmacy instance

    Returns:
        List of Tool instances
    """
    tools_instance = PharmacyTools(pharmacy)

    # Create Tool instances that properly wrap the methods
    return [
        Tool(
            name="get_prescriptions",
            description="Retrieves prescription data for the pharmacy",
            func=tools_instance.get_prescriptions,
        ),
        Tool(
            name="get_pharmacy_details",
            description="Gets specific pharmacy field information. Args: field (str) - The field to retrieve (name, phone, email, city, state)",
            func=tools_instance.get_pharmacy_details,
        ),
        Tool(
            name="get_pharmacy_summary",
            description="Get a complete summary of the pharmacy",
            func=tools_instance.get_pharmacy_summary,
        ),
    ]
