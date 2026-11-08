# ==============================================================================
# YATRA AI — Multi-Stage Production Dockerfile
# Stage 1: Build modern React frontend
# Stage 2: Minimalist Python 3.11 backend runtime
# ==============================================================================

# STAGE 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# STAGE 2: Python Production Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOKY_MAX_CPU_COUNT=4 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend, machine learning core, configurations, and models
COPY ml/ ./ml/
COPY backend/ ./backend/
COPY config/ ./config/
COPY results/models/ ./results/models/
COPY data/processed/ ./data/processed/
COPY data/raw/railways/stations.json ./data/raw/railways/stations.json
COPY data/raw/flights/Clean_flight_data_Vivek.csv ./data/raw/flights/Clean_flight_data_Vivek.csv
COPY .env.example .env

# Copy compiled frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose HTTP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch production server via Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

