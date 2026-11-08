"""
Recommendation Pydantic Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.auth import TravelDNASchema


class RecommendRequest(BaseModel):
    origin_city: str = Field(..., example="Delhi", description="Origin metropolitan cluster")
    destination_city: str = Field(..., example="Mumbai", description="Destination metropolitan cluster")
    departure_window: Optional[str] = Field(default="Morning", example="Morning", description="Early Morning, Morning, Afternoon, Evening, Night")
    trip_purpose: Optional[str] = Field(default="Leisure", example="Business", description="Business, Leisure, Commute, Family")
    party_size: Optional[int] = Field(default=1, ge=1, le=10, description="Number of passengers")
    lead_days: Optional[int] = Field(default=14, ge=0, le=120, description="Days between booking and travel")
    travel_date: Optional[str] = Field(default=None, example="2024-04-15", description="Optional travel date string (YYYY-MM-DD)")
    travel_dna: Optional[TravelDNASchema] = Field(default_factory=TravelDNASchema, description="7-D Travel DNA preferences")
    seed: Optional[int] = Field(default=None, description="Optional seed for deterministic candidate retrieval")


class QualityScoresSchema(BaseModel):
    cost: float
    time: float
    reliability: float
    comfort: float
    carbon: float
    departure_fit: float


class ItineraryItemSchema(BaseModel):
    rank: int
    is_recommended: bool
    preference_threshold_met: bool
    ml_personalization_score: float
    mode: str
    carrier: str
    service_identifier: str
    service_tier: str
    departure_window: str
    cost_inr: float
    duration_hours: float
    distance_km: float
    transfer_count: int
    carbon_estimate_kg: float
    historical_punctuality_rate: float
    relative_quality_scores: QualityScoresSchema
    feature_reasons: List[str]


class SearchQuerySchema(BaseModel):
    origin_city: str
    destination_city: str
    departure_window: str
    trip_purpose: str
    party_size: int
    lead_days: int
    travel_date: Optional[str] = None


class ScoringMetadataSchema(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_family: str
    feature_configuration: str
    decision_threshold: float
    ranking_method: str


class RecommendResponse(BaseModel):
    status: str
    session_id: Optional[int] = None
    search_query: SearchQuerySchema
    traveller_dna: Dict[str, float]
    total_candidates: int
    recommended_journey: Optional[ItineraryItemSchema] = None
    itineraries: List[ItineraryItemSchema]
    scoring_metadata: ScoringMetadataSchema

