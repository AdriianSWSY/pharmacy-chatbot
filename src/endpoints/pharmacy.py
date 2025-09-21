"""
API endpoints for pharmacy operations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
import logging
from src.models.pharmacy import Pharmacy
from src.services.pharmacy_service import PharmacyService
from src.clients.pharmacy_api import PharmacyAPIClient
from config.settings import settings
from src.endpoints.swagger.pharmacy_docs import (
    PHARMACY_SEARCH_RESPONSES,
    PHONE_SEARCH_PARAM_DOC,
    PHARMACY_ENDPOINTS_DOC,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_pharmacy_service() -> PharmacyService:
    """
    Dependency injection for pharmacy service.

    Returns:
        PharmacyService instance
    """
    # Create API client and service using configuration settings
    api_client = PharmacyAPIClient(
        base_url=settings.pharmacy_api.base_url,
        timeout=settings.pharmacy_api.timeout,
        retry_count=settings.pharmacy_api.retry_count,
        retry_delay=settings.pharmacy_api.retry_delay,
    )

    return PharmacyService(api_client=api_client)


@router.get(
    "/pharmacies",
    response_model=List[Pharmacy],
    summary=PHARMACY_ENDPOINTS_DOC["get_all_pharmacies"]["summary"],
)
async def get_all_pharmacies(
    service: PharmacyService = Depends(get_pharmacy_service),
) -> List[Pharmacy]:
    """
    Retrieve all pharmacy companies with their prescriptions.

    Returns:
        List of pharmacy objects with their details and prescriptions.

    Raises:
        HTTPException: 503 if the service is temporarily unavailable
    """
    try:
        pharmacies = await service.get_all_pharmacies()
        return pharmacies
    except Exception as e:
        logger.error(f"Failed to retrieve pharmacies: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        )


@router.get(
    "/pharmacies/search",
    response_model=Optional[Pharmacy],
    summary=PHARMACY_ENDPOINTS_DOC["search_pharmacy_by_phone"]["summary"],
    responses=PHARMACY_SEARCH_RESPONSES,
)
async def search_pharmacy_by_phone(
    phone: str = Query(
        ...,
        description=PHONE_SEARCH_PARAM_DOC["description"],
        example=PHONE_SEARCH_PARAM_DOC["example"],
    ),
    service: PharmacyService = Depends(get_pharmacy_service),
) -> Optional[Pharmacy]:
    """
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
    """
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required")

    try:
        pharmacy = await service.search_by_phone(phone)

        if pharmacy is None:
            # Return 404 for clarity that pharmacy wasn't found
            raise HTTPException(
                status_code=404, detail=f"No pharmacy found with phone number: {phone}"
            )

        return pharmacy

    except ValueError as e:
        # Invalid phone format
        logger.warning(f"Invalid phone format provided: {phone}")
        raise HTTPException(
            status_code=400, detail=f"Invalid phone number format: {str(e)}"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Failed to search pharmacy: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        )
