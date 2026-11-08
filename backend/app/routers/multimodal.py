"""
YĀTRĀ AI — Multimodal Journey & Location Router
Provides:
- POST /multimodal/plan: Full multimodal journey planning & ranking
- GET /locations/autocomplete: Real-time place & transit hub autocomplete
- GET /corridors/popular: Interactive corridors with coordinates
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
import logging

from backend.app.schemas.multimodal import PlanMultimodalRequest, LocationItemSchema
from backend.app.services.location_service import location_service
from backend.app.services.multimodal_composer import multimodal_composer

logger = logging.getLogger("yatra.multimodal_router")

router = APIRouter(prefix="", tags=["Multimodal Journey Planning & Geo Resolution"])


@router.post("/multimodal/plan")
def plan_multimodal_journey(req: PlanMultimodalRequest):
    """
    Multimodal Journey Planning:
    1. Resolves origin, destination & intermediate stops to exact geographic coordinates and transit hubs.
    2. Enforces hard operational constraints.
    3. Retrieves authentic mainline transport candidates from canonical datasets.
    4. Composes door-to-door first-mile, mainline, and last-mile legs with real connections.
    5. Evaluates Connection Guardian risk for all connections.
    6. Ranks complete multimodal journeys based on user's primary/secondary preferences & ML choice model.
    """
    try:
        result = multimodal_composer.plan_multimodal_journey(
            origin_query=req.origin,
            destination_query=req.destination,
            intermediate_stops=req.intermediate_stops,
            departure_window=req.departure_window or "Morning",
            travel_date=req.travel_date,
            party_size=req.party_size or 1,
            lead_days=req.lead_days or 14,
            primary_preference=req.primary_preference or "balanced",
            secondary_preference=req.secondary_preference,
            travel_class=req.travel_class,
            travel_dna=req.travel_dna,
            seed=req.seed,
        )
        return result
    except Exception as e:
        logger.error("Multimodal journey planning error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Journey planning error: {str(e)}",
        )


@router.get("/locations/autocomplete", response_model=List[Dict[str, Any]])
def autocomplete_locations(
    q: str = Query("", description="Search term for city, station, airport or landmark"),
    category: Optional[str] = Query(None, description="Optional category filter (city, rail_station, airport, bus_terminal, landmark)"),
    limit: int = Query(8, ge=1, le=20),
):
    """
    Location & Transit Hub Autocomplete:
    Matches Indian railway stations (IRCTC codes), domestic/intl airports (IATA),
    intercity bus terminals, landmarks, and metropolitan clusters.
    """
    return location_service.autocomplete(query=q, category=category, limit=limit)


@router.get("/corridors/popular")
def get_popular_corridors():
    """
    Returns prominent intercity corridors with full geographic coordinates
    for map-first exploration.
    """
    return {
        "status": "success",
        "corridors": location_service.get_supported_corridors_with_coords(),
    }

