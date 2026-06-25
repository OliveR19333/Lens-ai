"""FastAPI application entry point (spec §4).

Run with::

    uvicorn app.main:app --reload --port 8080

Interactive docs at ``/docs``.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.routers import auth, counties, geocode, missions, parcels, projects, sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gas")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Backend for the GAS Property Mapping System — address → geocode → "
        "parcel lookup → DJI KMZ mission → WebODM processing → scaled print maps."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spec §4.2 endpoint groups.
app.include_router(auth.router)
app.include_router(counties.router)
app.include_router(geocode.router)
app.include_router(parcels.router)
app.include_router(missions.router)
app.include_router(projects.router)
app.include_router(sync.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "service": settings.app_name, "version": __version__}


@app.on_event("startup")
def _startup() -> None:
    logger.info("%s v%s starting (env=%s)", settings.app_name, __version__, settings.env)
    # DB init is intentionally not called automatically here — run Alembic
    # migrations (or app.database.init_db()) explicitly during deployment so a
    # missing/locked PostGIS instance doesn't block app boot in the field.
