"""
Saved Trips & Bookmarks Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import User, SavedTrip
from backend.app.schemas.trip import SaveTripRequest, SavedTripResponse
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/trips", tags=["Saved Trips & Bookmarks"])


@router.post("", response_model=SavedTripResponse, status_code=status.HTTP_201_CREATED)
def save_trip(
    req: SaveTripRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Saves a recommended journey to the authenticated user's saved trips."""
    trip = SavedTrip(
        user_id=user.id,
        session_id=req.session_id,
        origin_city=req.origin_city,
        destination_city=req.destination_city,
        mode=req.mode,
        carrier=req.carrier,
        service_identifier=req.service_identifier,
        service_tier=req.service_tier,
        cost_inr=req.cost_inr,
        duration_hours=req.duration_hours,
        departure_window=req.departure_window,
        notes=req.notes,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("", response_model=List[SavedTripResponse])
def get_user_saved_trips(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all saved trips for the authenticated user."""
    trips = (
        db.query(SavedTrip)
        .filter(SavedTrip.user_id == user.id)
        .order_by(SavedTrip.created_at.desc())
        .all()
    )
    return trips


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_trip(
    trip_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a saved trip by ID for the authenticated user."""
    trip = (
        db.query(SavedTrip)
        .filter(SavedTrip.id == trip_id, SavedTrip.user_id == user.id)
        .first()
    )
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved trip ID {trip_id} not found.",
        )
    db.delete(trip)
    db.commit()
    return None

