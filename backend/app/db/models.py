"""
YATRA AI — SQLAlchemy Database Models
Persistent storage for:
- Users & hashed credentials
- Search sessions & Travel DNA preferences
- ML ranked itinerary recommendations
- User choice feedback (Closed-loop ML tracking)
- Saved trips & bookmarks
"""

import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    travel_dna_json = Column(Text, nullable=True)  # JSON-encoded 7-D Travel DNA preferences
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    sessions = relationship("SearchSession", back_populates="user", cascade="all, delete-orphan")
    saved_trips = relationship("SavedTrip", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("UserChoiceFeedback", back_populates="user", cascade="all, delete-orphan")


class SearchSession(Base):
    __tablename__ = "search_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    origin_city = Column(String(64), nullable=False)
    destination_city = Column(String(64), nullable=False)
    departure_window = Column(String(32), default="Morning")
    trip_purpose = Column(String(32), default="Leisure")
    party_size = Column(Integer, default=1)
    lead_days = Column(Integer, default=14)
    travel_date = Column(String(32), nullable=True)
    travel_dna_json = Column(Text, nullable=False)
    total_candidates = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    itineraries = relationship("RecommendedItinerary", back_populates="session", cascade="all, delete-orphan")
    feedback = relationship("UserChoiceFeedback", back_populates="session", uselist=False, cascade="all, delete-orphan")


class RecommendedItinerary(Base):
    __tablename__ = "recommended_itineraries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("search_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    is_recommended = Column(Boolean, default=False)
    preference_threshold_met = Column(Boolean, default=False)
    ml_personalization_score = Column(Float, nullable=False)
    mode = Column(String(32), nullable=False)
    carrier = Column(String(128), nullable=False)
    service_identifier = Column(String(64), nullable=False)
    service_tier = Column(String(64), nullable=False)
    departure_window = Column(String(32), nullable=False)
    cost_inr = Column(Float, nullable=False)
    duration_hours = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    transfer_count = Column(Integer, default=0)
    carbon_estimate_kg = Column(Float, default=0.0)
    historical_punctuality_rate = Column(Float, default=0.85)
    relative_quality_scores_json = Column(Text, nullable=True)
    feature_reasons_json = Column(Text, nullable=True)

    # Relationships
    session = relationship("SearchSession", back_populates="itineraries")


class SavedTrip(Base):
    __tablename__ = "saved_trips"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(Integer, nullable=True)
    origin_city = Column(String(64), nullable=False)
    destination_city = Column(String(64), nullable=False)
    mode = Column(String(32), nullable=False)
    carrier = Column(String(128), nullable=False)
    service_identifier = Column(String(64), nullable=False)
    service_tier = Column(String(64), nullable=False)
    cost_inr = Column(Float, nullable=False)
    duration_hours = Column(Float, nullable=False)
    departure_window = Column(String(32), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_trips")


class UserChoiceFeedback(Base):
    """
    Closed-Loop ML tracking record:
    Logs whether the user selected the #1 recommended journey, an alternative rank, or rejected the set.
    """
    __tablename__ = "user_choice_feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("search_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    selected_rank = Column(Integer, nullable=False)
    selected_mode = Column(String(32), nullable=False)
    action_type = Column(String(32), default="selected")  # selected, rejected, bookmarked
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    session = relationship("SearchSession", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")

