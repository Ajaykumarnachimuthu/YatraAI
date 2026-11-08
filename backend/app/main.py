"""
YATRA AI — FastAPI Production Application Server
Modular microservice orchestration connecting:
- Machine Learning inference core (champion_gb_core.joblib)
- Relational Database persistence (PostgreSQL / SQLite WAL)
- High-speed Redis caching & rate limiting
- JWT authentication & 7-D Travel DNA profile persistence
- Closed-loop choice feedback tracking
- Modern Single Page Web Application serving
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

# Silence joblib/loky Windows CPU count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.config import settings
from backend.app.db.session import init_db
from backend.app.routers import (
    health_router,
    auth_router,
    corridors_router,
    personas_router,
    recommendations_router,
    feedback_router,
    trips_router,
    multimodal_router,
)

# Ensure database tables exist immediately on module load
init_db()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("yatra.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: initializes DB schemas and pre-warms ML engine."""
    logger.info("Initializing Yatra AI database schemas...")
    init_db()

    logger.info("Pre-warming ML recommendation engine and transit graph...")
    try:
        from ml.recommendation_engine import get_recommendation_engine
        get_recommendation_engine()
        logger.info("ML recommendation engine successfully warmed up.")
    except Exception as e:
        logger.warning("ML engine warmup deferred: %s", str(e))

    yield
    logger.info("Yatra AI application shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade Multimodal Transit Orchestration Engine powered by 7-D Travel DNA & HistGradientBoosting ML.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(corridors_router, prefix=settings.API_V1_PREFIX)
app.include_router(personas_router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendations_router, prefix=settings.API_V1_PREFIX)
app.include_router(feedback_router, prefix=settings.API_V1_PREFIX)
app.include_router(trips_router, prefix=settings.API_V1_PREFIX)
app.include_router(multimodal_router, prefix=settings.API_V1_PREFIX)

# Static file serving & Frontend SPA fallback
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
SRC_WEB = os.path.join(BASE_DIR, "src", "web")

# Always mount /static for static assets
if os.path.exists(SRC_WEB):
    app.mount("/static", StaticFiles(directory=SRC_WEB), name="static")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

elif os.path.exists(SRC_WEB):
    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(SRC_WEB, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

