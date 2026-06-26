"""ORM models (spec §11 — Data Model).

The ``Project`` table is the heart of the system: it tracks one property mapping
job from address entry through to printed maps.
"""
from __future__ import annotations

import datetime as dt
import enum
import uuid

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """Application user (spec §12 — multi-user / Devan Teaster access)."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )


class County(str, enum.Enum):
    blount = "blount"
    knox = "knox"
    sevier = "sevier"


class ProjectStatus(str, enum.Enum):
    setup = "setup"
    mission_ready = "mission_ready"
    flying = "flying"
    processing = "processing"
    complete = "complete"


class UseCase(str, enum.Enum):
    irrigation = "irrigation"
    hardscape = "hardscape"
    both = "both"


class Project(Base):
    """A single property mapping job (spec §11.1)."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )
    address: Mapped[str] = mapped_column(String(512))
    county: Mapped[County | None] = mapped_column(Enum(County), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    parcel_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parcel_geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.setup
    )

    # Artifact file paths (spec §11.1).
    mission_kmz: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ortho_tif: Mapped[str | None] = mapped_column(String(512), nullable=True)
    dsm_tif: Mapped[str | None] = mapped_column(String(512), nullable=True)
    dtm_tif: Mapped[str | None] = mapped_column(String(512), nullable=True)
    features_geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    map_flat_pdf: Mapped[str | None] = mapped_column(String(512), nullable=True)
    map_elev_pdf: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # WebODM linkage (spec §7).
    webodm_project_id: Mapped[int | None] = mapped_column(nullable=True)
    webodm_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Manual annotation layer (spec §12) — kept separate from AI features so
    # re-running detection never clobbers operator edits.
    annotations_geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    print_scale: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    use_case: Mapped[UseCase] = mapped_column(Enum(UseCase), default=UseCase.both)

    # Project history / archive (spec §12).
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_username: Mapped[str | None] = mapped_column(String(64), nullable=True)


class CountyCache(Base):
    """Per-county parcel bundle metadata for PWA offline sync (spec §5.2)."""

    __tablename__ = "county_cache"

    county: Mapped[County] = mapped_column(Enum(County), primary_key=True)
    version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parcel_count: Mapped[int] = mapped_column(default=0)
    bundle_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bundle_size_bytes: Mapped[int] = mapped_column(default=0)
    last_synced_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
