"""
Utility functions for phone number operations.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize phone number for comparison.

    Args:
        phone: Phone number to normalize

    Returns:
        Normalized phone number (digits only) or None if invalid

    Examples:
        >>> normalize_phone("(555) 123-4567")
        "5551234567"
        >>> normalize_phone("1-555-123-4567")
        "5551234567"
        >>> normalize_phone("")
        None
        >>> normalize_phone("123")  # Too short
        None
    """
    if not phone:
        logger.debug("Empty phone number provided")
        return None

    # Remove all non-digit characters
    normalized = re.sub(r"\D", "", phone)

    if not normalized:
        logger.debug(f"No digits found in phone number: {phone}")
        return None

    # Remove country code if present (assuming US numbers starting with 1)
    if len(normalized) == 11 and normalized.startswith("1"):
        normalized = normalized[1:]

    # Validate US phone number length (10 digits)
    if len(normalized) != 10:
        logger.warning(
            f"Invalid phone number length: {len(normalized)} digits in '{phone}'"
        )
        return None

    # Validate area code (first 3 digits shouldn't start with 0 or 1)
    if normalized[0] in ("0", "1"):
        logger.warning(f"Invalid area code in phone number: {normalized[:3]}")
        return None

    # Validate exchange code (digits 4-6 shouldn't start with 0 or 1)
    if normalized[3] in ("0", "1"):
        logger.warning(f"Invalid exchange code in phone number: {normalized[3:6]}")
        return None

    return normalized
