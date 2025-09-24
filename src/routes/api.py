from fastapi import APIRouter
from src.endpoints import health, pharmacy, websocket

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(pharmacy.router, prefix="/api", tags=["pharmacy"])
api_router.include_router(websocket.router, tags=["websocket"])
