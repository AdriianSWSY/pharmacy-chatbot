from fastapi import APIRouter
from src.endpoints import health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])