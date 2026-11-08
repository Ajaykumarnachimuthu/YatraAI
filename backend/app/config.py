"""
YATRA AI — Backend Application Configuration
Twelve-Factor environment management via Pydantic Settings.
"""

import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Yātrā AI — Intelligent Multimodal Transit"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "development", "dev")
        return bool(v)

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database (anchored to BASE_DIR so working directory changes don't affect DB path)
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'yatra_ai.db')}"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def resolve_sqlite_path(cls, v: str) -> str:
        if v.startswith("sqlite:///") and not (len(v) > 12 and v[11] == ":"):
            # If relative path, anchor to BASE_DIR
            rel_path = v[10:]
            if rel_path.startswith("./") or rel_path.startswith(".\\"):
                rel_path = rel_path[2:]
            if not os.path.isabs(rel_path):
                return f"sqlite:///{os.path.join(BASE_DIR, rel_path)}"
        return v

    # Caching & Rate Limiting
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_PER_MINUTE: int = 60

    # Authentication & Security
    JWT_SECRET_KEY: str = "yatra_ai_super_secret_jwt_key_production_grade_32_bytes_min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Hours

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    # Machine Learning Core
    CHAMPION_MODEL_PATH: str = os.path.join(BASE_DIR, "results", "models", "champion_gb_core.joblib")
    CONFIG_PATH: str = os.path.join(BASE_DIR, "config", "synthetic_generation.yaml")
    DECISION_THRESHOLD: float = 0.30

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

