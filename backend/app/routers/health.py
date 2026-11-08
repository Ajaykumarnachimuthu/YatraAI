"""
Health & System Status Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.services.recommendation_service import recommendation_service
from backend.app.services.cache_service import cache_service

router = APIRouter(prefix="/health", tags=["Health & System Telemetry"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive system health check:
    - Verifies ML Champion Model initialization and decision threshold (tau=0.30)
    - Verifies Relational Database connectivity (SQLite / PostgreSQL)
    - Verifies Cache status (Redis or In-Memory LRU)
    - Verifies Multimodal Transit Corridors coverage
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    ml_engine = recommendation_service.get_ml_engine()
    corridors = recommendation_service.get_corridors()

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "Yatra AI Intelligent Multimodal Recommendation Service",
        "version": "2.0.0",
        "model_family": "HistGradientBoostingClassifier",
        "feature_configuration": ml_engine.engine.feature_config,
        "decision_threshold": ml_engine.engine.threshold,
        "supported_metro_hubs": len(corridors["metro_cities"]),
        "database_status": db_status,
        "cache_backend": "redis" if cache_service.redis_client else "in_memory_lru",
        "machine_learning": {
            "model_family": "HistGradientBoostingClassifier",
            "feature_configuration": ml_engine.engine.feature_config,
            "decision_threshold": ml_engine.engine.threshold,
            "features_count": 28,
            "supported_metro_hubs": len(corridors["metro_cities"]),
            "directed_corridors_count": corridors["corridors_count"],
        },
    }
