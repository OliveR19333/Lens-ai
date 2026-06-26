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

    auth → create project → submit task → poll until COMPLETED → download
    orthophoto/dsm/dtm → persist paths on Project → trigger feature detection
    and map rendering.
    """
    from pathlib import Path

    from app.database import SessionLocal
    from app.models import Project, ProjectStatus
    from app.services.webodm import WebODMClient, WebODMError
    from app.storage import project_dir

    db = SessionLocal()
    try:
        project = db.get(Project, project_id)
        if not project:
            return {"project_id": project_id, "status": "error", "error": "project not found"}
        project.status = ProjectStatus.processing
        db.commit()

        client = WebODMClient()
        dest = project_dir(project_id) / "webodm"
        try:
            outputs = client.run_pipeline(f"GAS_{project_id}", image_paths, Path(dest))
        except WebODMError as exc:
            logger.exception("WebODM pipeline failed for %s", project_id)
            return {"project_id": project_id, "status": "error", "error": str(exc)}

        project.ortho_tif = outputs.get("ortho.tif")
        project.dsm_tif = outputs.get("dsm.tif")
        project.dtm_tif = outputs.get("dtm.tif")
        project.webodm_project_id = int(outputs["_webodm_project_id"])
        project.webodm_task_id = outputs["_webodm_task_id"]
        db.commit()
        logger.info("WebODM done for %s: %s", project_id, list(outputs))

        # Chain: AI features (best-effort) → render maps from the real ortho/DEM.
        detect_features.delay(project_id)
        render_maps.delay(project_id)
        return {"project_id": project_id, "status": "processed", "assets": list(outputs)}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.detect_features", bind=True)
def detect_features(self, project_id: str) -> dict:
    """Run AI feature detection on a project's orthomosaic (spec §8).

    Loads the project's ortho/DTM, runs the detection pipeline, and stores the
    resulting FeatureCollection on Project.features_geojson so both maps can
    label the detected ponds/trees/structures/driveways/slope.
    """
    from app.database import SessionLocal
    from app.models import Project
    from app.services import feature_detection

    db = SessionLocal()
    try:
        project = db.get(Project, project_id)
        if not project or not project.ortho_tif:
            return {"project_id": project_id, "status": "skipped", "reason": "no orthomosaic"}
        try:
            fc = feature_detection.detect_features(project.ortho_tif, project.dtm_tif)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Feature detection failed for %s", project_id)
            return {"project_id": project_id, "status": "error", "error": str(exc)}
        project.features_geojson = fc
        db.commit()
        n = len(fc.get("features", []))
        logger.info("detect_features(%s): %d features", project_id, n)
        return {"project_id": project_id, "status": "complete", "feature_count": n}
    finally:
        db.close()


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
