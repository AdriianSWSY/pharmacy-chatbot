import datetime
from fastapi import APIRouter
from pydantic import BaseModel
import os
from config.settings import settings


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime.datetime
    version: str
    environment: str
    api_base_url: str


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns the health status of the API service",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint that provides service status and basic information.

    Returns:
        HealthResponse with status, timestamp, version, and environment info
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        version=os.getenv("APP_VERSION", "1.0.0"),
        environment=settings.environment,
        api_base_url=settings.pharmacy_api.base_url,
    )
