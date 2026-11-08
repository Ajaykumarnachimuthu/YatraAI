"""
Feedback & Closed-Loop ML Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    session_id: int
    selected_rank: int = Field(..., ge=1, le=10, description="Rank of the chosen itinerary (1=Champion recommended)")
    selected_mode: str = Field(..., example="Rail", description="Rail or Flight")
    action_type: str = Field(default="selected", description="selected, rejected, bookmarked")
    user_comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    session_id: int
    selected_rank: int
    action_type: str
    message: str = "Choice feedback recorded for closed-loop model optimization."

    class Config:
        from_attributes = True

