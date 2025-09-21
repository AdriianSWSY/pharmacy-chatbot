"""
Swagger/OpenAPI documentation package for endpoints.

This package contains external documentation files for FastAPI endpoints,
separating the documentation from the endpoint logic for better organization
and maintainability.
"""

from .pharmacy_docs import (
    PHARMACY_SEARCH_RESPONSES,
    PHONE_SEARCH_PARAM_DOC,
    PHARMACY_ENDPOINTS_DOC,
)

__all__ = [
    "PHARMACY_SEARCH_RESPONSES",
    "PHONE_SEARCH_PARAM_DOC",
    "PHARMACY_ENDPOINTS_DOC",
]
