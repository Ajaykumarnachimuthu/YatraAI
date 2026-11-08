"""
Persona Archetypes & Travel DNA Router
"""

from fastapi import APIRouter
from backend.app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/personas", tags=["Personas & Travel DNA"])


@router.get("")
def get_personas():
    """Lists the 6 calibrated traveller persona archetypes and their default 7-D Travel DNA vectors."""
    return {"personas": recommendation_service.get_personas()}

