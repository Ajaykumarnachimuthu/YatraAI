"""
YĀTRĀ AI — Multimodal Journey Pydantic Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PlanMultimodalRequest(BaseModel):
    origin: str = Field(..., example="Connaught Place, Delhi", description="Starting place, station, airport or landmark")
    destination: str = Field(..., example="Bandra Kurla Complex, Mumbai", description="Destination place, station, airport or landmark")
    intermediate_stops: Optional[List[str]] = Field(default=[], description="Optional intermediate stops")
    departure_window: Optional[str] = Field(default="Morning", example="Morning")
    travel_date: Optional[str] = Field(default=None, example="2026-11-15")
    return_date: Optional[str] = Field(default=None, example="2026-11-20")
    party_size: Optional[int] = Field(default=1, ge=1, le=10)
    lead_days: Optional[int] = Field(default=14, ge=0, le=120)
    primary_preference: Optional[str] = Field(default="balanced", example="fastest")
    secondary_preference: Optional[str] = Field(default=None, example="eco_friendly")
    travel_class: Optional[str] = Field(default="All", example="AC / Business")
    travel_dna: Optional[Dict[str, float]] = Field(default=None)
    seed: Optional[int] = Field(default=None)


class LocationItemSchema(BaseModel):
    id: str
    name: str
    category: str
    city: str
    state: Optional[str] = None
    code: Optional[str] = None
    lat: float
    lng: float
    description: Optional[str] = None

