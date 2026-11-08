"""
YATRA AI — Database Engine & Session Factory
Supports PostgreSQL for production and SQLite (WAL mode) for zero-setup local execution.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.config import settings
from backend.app.db.base import Base

# Ensure SQLite path directory exists if using SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

    # Enable SQLite foreign key constraints and WAL journal mode
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes all database tables defined in models."""
    import backend.app.db.models  # Ensure models are imported
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency yielding database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

