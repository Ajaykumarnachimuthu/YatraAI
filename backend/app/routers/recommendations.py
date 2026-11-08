"""
Personalized Multi-Modal Recommendation Router
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.schemas.recommendation import RecommendRequest, RecommendResponse
from backend.app.services.recommendation_service import recommendation_service
from backend.app.dependencies import get_optional_user

router = APIRouter(prefix="", tags=["Personalized Journey Recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend_journey(
    req: RecommendRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Personalized Multi-Modal Journey Recommendation:
    1. Validates operational hard constraints.
    2. Retrieves real multimodal candidate alternatives from canonical datasets.
    3. Normalizes pre-choice quality scores across the candidate set.
    4. Evaluates pointwise choice probabilities via frozen HistGradientBoosting champion model.
    5. Ranks candidates descending by ML probability.
    6. Attaches honest, feature-derived recommendation explanations.
    7. Persists search session & ranked alternatives to relational database.
    """
    query = {
        "origin_city": req.origin_city.strip(),
        "destination_city": req.destination_city.strip(),
        "departure_window": req.departure_window,
        "trip_purpose": req.trip_purpose,
        "party_size": req.party_size,
        "lead_days": req.lead_days,
        "travel_date": req.travel_date,
    }

    dna_dict = req.travel_dna.model_dump() if req.travel_dna else {}

    # If authenticated user has saved DNA and request used all defaults, optionally apply user's saved DNA
    if user and user.travel_dna_json and not req.travel_dna:
        try:
            dna_dict = json.loads(user.travel_dna_json)
        except Exception:
            pass

    user_id = user.id if user else None

    try:
        result = recommendation_service.recommend_and_persist(
            query=query,
            traveller_dna=dna_dict,
            db=db,
            user_id=user_id,
            seed=req.seed,
        )
        return result
    except recommendation_service.HardConstraintViolation as hcv:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(hcv))
    except Exception as err:
        logger.error("Recommendation processing failure: %s", str(err), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation processing error: {str(err)}",
        )

