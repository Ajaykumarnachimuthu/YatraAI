"""
Closed-Loop ML Feedback Router
Tracks traveller choice events (acceptances, alternatives selected, rejections)
to fuel continuous preference learning.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.db.models import User, SearchSession, UserChoiceFeedback
from backend.app.schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from backend.app.dependencies import get_optional_user

router = APIRouter(prefix="/feedback", tags=["Closed-Loop ML Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def record_choice_feedback(
    req: FeedbackCreateRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Records a traveller choice decision for an existing search session.
    Enables online evaluation of champion model precision in production.
    """
    session = db.query(SearchSession).filter(SearchSession.id == req.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search session ID {req.session_id} not found.",
        )

    feedback = UserChoiceFeedback(
        session_id=req.session_id,
        user_id=user.id if user else None,
        selected_rank=req.selected_rank,
        selected_mode=req.selected_mode,
        action_type=req.action_type,
        user_comment=req.user_comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse(
        id=feedback.id,
        session_id=feedback.session_id,
        selected_rank=feedback.selected_rank,
        action_type=feedback.action_type,
        message="Choice feedback recorded for closed-loop model optimization.",
    )


@router.get("/summary")
def get_feedback_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Summarizes production choice adoption:
    Quantifies the percentage of sessions where Rank #1 (Champion Recommendation) was adopted.
    """
    total_feedbacks = db.query(func.count(UserChoiceFeedback.id)).scalar() or 0
    rank1_count = (
        db.query(func.count(UserChoiceFeedback.id))
        .filter(UserChoiceFeedback.selected_rank == 1)
        .scalar()
        or 0
    )

    adoption_rate = (rank1_count / total_feedbacks) if total_feedbacks > 0 else 0.0

    return {
        "total_feedback_events": total_feedbacks,
        "champion_rank_1_selections": rank1_count,
        "champion_adoption_rate": round(adoption_rate, 4),
        "target_operational_precision": 0.4323,
    }

