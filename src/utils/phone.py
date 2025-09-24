"""
Simple phone number normalization utility.

This module provides a simple function to normalize phone numbers
by extracting only the digits for comparison purposes.
"""

import re
from typing import Optional


def normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize phone number by extracting only digits.

    Args:
        phone: Phone number string in any format

    Returns:
        String containing only digits, or None if no digits found

    Examples:
        >>> normalize_phone("(555) 123-4567")
        "5551234567"
        >>> normalize_phone("1-555-123-4567")
        "15551234567"
        >>> normalize_phone("555.123.4567")
        "5551234567"
        >>> normalize_phone("")
        None
        >>> normalize_phone("no numbers here")
        None
    """
    if not phone:
        return None

    # Extract only digits from the phone string
    digits = re.sub(r"\D", "", phone)

    # Return None if no digits were found
    if not digits:
        return None

    # Remove leading '1' if it's 11 digits (US country code)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    return digits
