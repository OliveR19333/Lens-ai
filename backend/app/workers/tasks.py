"""Celery tasks: WebODM processing, feature detection, map render, parcel sync.

⚙ Phase 2/3 orchestration. Each task strings together the (stubbed) services in
the order the spec describes; the heavy lifting lives in those services and is
marked TODO there. Tasks are written to be idempotent and to advance the
``Project.status`` state machine (spec §11.1).
"""
from __future__ import annotations

import logging
from typing import List

from app.gis import county_sync
from app.gis.county_sync import COUNTY_SOURCES
from app.workers.celery_app import celery_app

logger = logging.getLogger("gas.tasks")


@celery_app.task(name="app.workers.tasks.process_webodm_job", bind=True)
def process_webodm_job(self, project_id: str, image_paths: List[str]) -> dict:
    """Drive a WebODM job end-to-end (spec §7.2), then fetch ortho + DEM.

    ⚙ TODO: authenticate → create project → submit task → poll until COMPLETED
    → download orthophoto/dsm/dtm → persist paths on Project → set status.
    """
    logger.info("process_webodm_job(%s) — %d images — STUB", project_id, len(image_paths))
    return {"project_id": project_id, "images": len(image_paths), "status": "stub"}


@celery_app.task(name="app.workers.tasks.detect_features", bind=True)
def detect_features(self, project_id: str) -> dict:
    """Run AI feature detection on a project's orthomosaic (spec §8).

    ⚙ TODO: load Project.ortho_tif/dtm_tif → feature_detection.detect_features
    → store FeatureCollection on Project.features_geojson.
    """
    logger.info("detect_features(%s) — STUB", project_id)
    return {"project_id": project_id, "status": "stub"}


@celery_app.task(name="app.workers.tasks.render_maps", bind=True)
def render_maps(self, project_id: str) -> dict:
    """Render Map 1 (flat) and Map 2 (elevation) PDFs (spec §9).

    Renders from the project's parcel boundary + any available ortho/DEM +
    detected features, persists the PDF paths and locked print scale, and marks
    the project complete. Works with parcel-only data (no drone imagery yet):
    the maps render as scaled grid sheets.
    """
    from app.database import SessionLocal
    from app.models import Project, ProjectStatus
    from app.services.maps.flat_map import render_flat_map
    from app.services.maps.elevation_map import render_elevation_map
    from app.storage import project_dir

    db = SessionLocal()
    try:
        project = db.get(Project, project_id)
        if not project or not project.parcel_geojson:
            return {"project_id": project_id, "status": "error", "error": "no parcel geojson"}

        out = project_dir(project_id)
        flat_pdf = out / "map_flat.pdf"
        elev_pdf = out / "map_elev.pdf"
        county = project.county.value if project.county else ""

        scale = render_flat_map(
            project.parcel_geojson, flat_pdf,
            ortho_tif=project.ortho_tif, features_geojson=project.features_geojson,
            address=project.address or "", county=county,
        )
        render_elevation_map(
            project.parcel_geojson, elev_pdf,
            dsm_tif=project.dsm_tif, dtm_tif=project.dtm_tif,
            features_geojson=project.features_geojson, address=project.address or "", county=county,
        )

        project.map_flat_pdf = str(flat_pdf)
        project.map_elev_pdf = str(elev_pdf)
        project.print_scale = scale.label
        project.status = ProjectStatus.complete
        db.commit()
        logger.info("render_maps(%s) complete — %s", project_id, scale.label)
        return {"project_id": project_id, "status": "complete", "print_scale": scale.label}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.sync_all_counties", bind=True)
def sync_all_counties(self) -> dict:
    """Monthly parcel sync across all enabled counties (spec §5.2)."""
    results = {}
    for key in COUNTY_SOURCES:
        try:
            results[key] = county_sync.sync_county(key).as_dict()
        except Exception as exc:  # keep going on per-county failure
            logger.exception("County %s sync failed", key)
            results[key] = {"status": "error", "error": str(exc)}
    return results
