"""
Swagger/OpenAPI documentation for pharmacy endpoints.
This module contains all the documentation that was previously inline in the endpoint file.
"""

from typing import Dict, Any

# Response examples for pharmacy search endpoint
PHARMACY_SEARCH_RESPONSES: Dict[int, Dict[str, Any]] = {
    200: {
        "description": "Successful search",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "name": "Acme Pharmacy",
                    "address": "123 Main St",
                    "phone": "555-1234",
                    "prescriptions": [
                        {"id": 1, "medication": "Aspirin", "quantity": 100}
                    ],
                }
            }
        },
    },
    400: {"description": "Invalid phone number format"},
    404: {"description": "Pharmacy not found"},
    503: {"description": "Service temporarily unavailable"},
}

# Parameter documentation
PHONE_SEARCH_PARAM_DOC = {
    "description": "Phone number to search for (accepts various formats like (555) 123-4567, 555-123-4567, 5551234567)",
    "example": "(555) 123-4567",
}

# Endpoint summaries and descriptions
PHARMACY_ENDPOINTS_DOC = {
    "get_all_pharmacies": {
        "summary": "Get all pharmacies",
        "description": """
        Retrieve all pharmacy companies with their prescriptions.

        Returns:
            List of pharmacy objects with their details and prescriptions.

        Raises:
            HTTPException: 503 if the service is temporarily unavailable
        """,
    },
    "search_pharmacy_by_phone": {
        "summary": "Search pharmacy by phone",
        "description": """
        Search for a pharmacy by phone number.

        Accepts various phone formats including:
        - (555) 123-4567
        - 555-123-4567
        - 5551234567
        - 1-555-123-4567

        Returns:
            Pharmacy object if found, None if not found.

        Raises:
            HTTPException:
                - 400 if phone number format is invalid
                - 404 if pharmacy is not found
                - 503 if service is temporarily unavailable
        """,
    },
}
