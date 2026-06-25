"""Application settings, loaded from environment / .env.

See ``.env.example`` for the full list of variables.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_name: str = "GAS Property Mapping System"
    env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080
    admin_username: str = "admin"
    admin_password: str = "change-me"

    # Database
    database_url: str = "postgresql+psycopg2://gas:gas@localhost:5432/gas_mapping"

    # Celery / Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    parcel_sync_cron_day: int = 1
    parcel_sync_cron_hour: int = 2

    # Geocoding
    census_geocoder_url: str = (
        "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    )
    census_benchmark: str = "2020"
    google_maps_api_key: str = ""

    # WebODM
    webodm_base_url: str = "http://localhost:8000/api"
    webodm_username: str = "admin"
    webodm_password: str = "change-me"

    # Feature detection
    yolo_model_path: str = "models/yolov8n-aerial-property.pt"
    feature_min_confidence: float = 0.45

    # Storage
    storage_dir: str = "./storage"
    data_dir: str = "./data"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (use as a FastAPI dependency)."""
    return Settings()
