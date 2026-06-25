"""SQLAlchemy engine / session wiring for PostgreSQL + PostGIS (spec §4.1).

The spatial parcel tables (``parcels_blount`` etc.) are populated by the monthly
GIS sync (spec §5.2) and queried via raw PostGIS SQL in ``services/parcels.py``;
the ORM models in ``models.py`` cover the application's own tables.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency yielding a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create application tables and ensure the PostGIS extension exists.

    Note: the per-county spatial parcel tables are created/managed by the GIS
    sync job, not here.
    """
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=engine)
