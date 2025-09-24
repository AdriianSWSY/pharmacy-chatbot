"""
Data models for pharmacy API integration.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Prescription(BaseModel):
    """Represents a prescription record for a pharmacy."""

    drug: str
    count: int


class Pharmacy(BaseModel):
    """Represents a pharmacy company with its details and prescriptions."""

    id: int
    name: str
    phone: str
    email: Optional[EmailStr] = None
    city: str
    state: str
    prescriptions: List[Prescription]
