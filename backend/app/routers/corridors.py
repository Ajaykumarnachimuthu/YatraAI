"""
Corridors & Metropolitan Network Router
"""

from fastapi import APIRouter
from backend.app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/corridors", tags=["Corridors & Transit Network"])


@router.get("")
def get_corridors():
    """Lists supported transit origin/destination metro hubs and directed corridors."""
    return recommendation_service.get_corridors()

