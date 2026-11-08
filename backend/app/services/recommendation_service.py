"""
YATRA AI — Recommendation Application Service
Coordinates:
- Machine Learning Recommendation Engine (ml.recommendation_engine)
- Relational Database persistence of SearchSessions & Itineraries
- Redis/In-memory caching of corridor and persona lookups
"""

import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.services.cache_service import cache_service
from backend.app.db.models import SearchSession, RecommendedItinerary

logger = logging.getLogger("yatra.recommendation_service")


class RecommendationService:
    def __init__(self):
        # Lazy import of ML recommendation engine to ensure rapid startup
        try:
            from ml.recommendation_engine import get_recommendation_engine, HardConstraintViolation
        except ImportError:
            from src.recommendation_engine import get_recommendation_engine, HardConstraintViolation

        self.get_ml_engine = get_recommendation_engine
        self.HardConstraintViolation = HardConstraintViolation

    def get_corridors(self) -> Dict[str, Any]:
        """Retrieves supported transit metro cities and directed corridors with caching."""
        cached = cache_service.get("yatra:supported_corridors")
        if cached:
            return cached

        engine = self.get_ml_engine()
        data = engine.get_supported_corridors()
        cache_service.set("yatra:supported_corridors", data, ttl_seconds=86400)
        return data

    def get_personas(self) -> List[Dict[str, Any]]:
        """Retrieves calibrated persona archetypes and Travel DNA moments with caching."""
        cached = cache_service.get("yatra:supported_personas")
        if cached:
            return cached

        engine = self.get_ml_engine()
        data = engine.get_supported_personas()
        cache_service.set("yatra:supported_personas", data, ttl_seconds=86400)
        return data

    def recommend_and_persist(
        self,
        query: Dict[str, Any],
        traveller_dna: Dict[str, float],
        db: Session,
        user_id: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executes true ML choice scoring, saves the search session and recommendations,
        and returns the formatted response.
        """
        engine = self.get_ml_engine()

        # Execute ML recommendation workflow
        result = engine.recommend(query=query, traveller_dna=traveller_dna, seed=seed)

        # Persist session and itineraries into database
        session_record = SearchSession(
            user_id=user_id,
            origin_city=query["origin_city"],
            destination_city=query["destination_city"],
            departure_window=query.get("departure_window", "Morning"),
            trip_purpose=query.get("trip_purpose", "Leisure"),
            party_size=int(query.get("party_size", 1)),
            lead_days=int(query.get("lead_days", 14)),
            travel_date=query.get("travel_date"),
            travel_dna_json=json.dumps(result["traveller_dna"]),
            total_candidates=result["total_candidates"],
        )
        db.add(session_record)
        db.flush()  # Obtain session_record.id

        # Persist candidate itineraries
        for it in result["itineraries"]:
            it_record = RecommendedItinerary(
                session_id=session_record.id,
                rank=it["rank"],
                is_recommended=it["is_recommended"],
                preference_threshold_met=it["preference_threshold_met"],
                ml_personalization_score=it["ml_personalization_score"],
                mode=it["mode"],
                carrier=it["carrier"],
                service_identifier=it["service_identifier"],
                service_tier=it["service_tier"],
                departure_window=it["departure_window"],
                cost_inr=it["cost_inr"],
                duration_hours=it["duration_hours"],
                distance_km=it["distance_km"],
                transfer_count=it["transfer_count"],
                carbon_estimate_kg=it["carbon_estimate_kg"],
                historical_punctuality_rate=it["historical_punctuality_rate"],
                relative_quality_scores_json=json.dumps(it["relative_quality_scores"]),
                feature_reasons_json=json.dumps(it["feature_reasons"]),
            )
            db.add(it_record)

        db.commit()

        # Attach session_id to returned payload
        result["session_id"] = session_record.id
        return result


recommendation_service = RecommendationService()

