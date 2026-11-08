"""
Saved Trips Schemas
"""

import datetime
from typing import Optional
from pydantic import BaseModel


class SaveTripRequest(BaseModel):
    session_id: Optional[int] = None
    origin_city: str
    destination_city: str
    mode: str
    carrier: str
    service_identifier: str
    service_tier: str
    cost_inr: float
    duration_hours: float
    departure_window: Optional[str] = None
    notes: Optional[str] = None


class SavedTripResponse(BaseModel):
    id: int
    origin_city: str
    destination_city: str
    mode: str
    carrier: str
    service_identifier: str
    service_tier: str
    cost_inr: float
    duration_hours: float
    departure_window: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

