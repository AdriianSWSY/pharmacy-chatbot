from fastapi import APIRouter
from src.endpoints import health, pharmacy

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(pharmacy.router, prefix="/api", tags=["pharmacy"])
