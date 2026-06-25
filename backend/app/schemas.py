"""Pydantic request/response schemas for the API (spec §4.2)."""
from __future__ import annotations

import datetime as dt
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---- Auth ----
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Counties ----
class CountyStatus(BaseModel):
    county: str
    county_name: str
    gis_portal_url: str
    version_hash: Optional[str] = None
    parcel_count: int = 0
    bundle_size_bytes: int = 0
    last_synced_at: Optional[dt.datetime] = None


# ---- Geocode ----
class GeocodeRequest(BaseModel):
    address: str


class GeocodeResponse(BaseModel):
    address: str
    lat: float
    lng: float
    county: Optional[str] = None
    county_name: Optional[str] = None
    source: str


# ---- Parcel ----
class ParcelLookupRequest(BaseModel):
    lat: float
    lng: float
    county: Optional[str] = Field(
        default=None, description="Optional county hint (blount|knox|sevier)."
    )


class ParcelResponse(BaseModel):
    parcel_id: Optional[str] = None
    owner: Optional[str] = None
    address: Optional[str] = None
    county: Optional[str] = None
    geojson: Optional[dict[str, Any]] = None


# ---- Mission ----
class MissionGenerateRequest(BaseModel):
    parcel_geojson: dict[str, Any]
    altitude_ft: float = 120.0
    forward_overlap: float = 0.80
    side_overlap: float = 0.75
    buffer_ft: float = 15.0
    project_id: Optional[str] = None


class MissionGenerateResponse(BaseModel):
    mission_id: str
    summary: dict[str, Any]
    kmz_url: str


# ---- Project ----
class ProjectCreateRequest(BaseModel):
    address: str
    county: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    parcel_id: Optional[str] = None
    parcel_geojson: Optional[dict[str, Any]] = None
    use_case: str = "both"
    notes: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    created_at: dt.datetime
    address: str
    county: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    parcel_id: Optional[str] = None
    status: str
    print_scale: Optional[str] = None
    use_case: str

    class Config:
        from_attributes = True


class ProjectStatusResponse(BaseModel):
    id: str
    status: str
    webodm_task_id: Optional[str] = None
    webodm_status: Optional[str] = None
    message: Optional[str] = None


class MapsResponse(BaseModel):
    id: str
    map_flat_pdf_url: Optional[str] = None
    map_elev_pdf_url: Optional[str] = None
    print_scale: Optional[str] = None
    ready: bool = False


# ---- Sync ----
class SyncResponse(BaseModel):
    triggered: bool
    task_id: Optional[str] = None
    message: str
