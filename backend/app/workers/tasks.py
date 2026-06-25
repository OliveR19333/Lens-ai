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

    ⚙ TODO: flat_map.render_flat_map + elevation_map.render_elevation_map →
    persist Project.map_flat_pdf/map_elev_pdf + print_scale → status=complete.
    """
    logger.info("render_maps(%s) — STUB", project_id)
    return {"project_id": project_id, "status": "stub"}


@celery_app.task(name="app.workers.tasks.sync_all_counties", bind=True)
def sync_all_counties(self) -> dict:
    """Monthly parcel sync across all enabled counties (spec §5.2)."""
    results = {}
    for key in COUNTY_SOURCES:
        try:
            results[key] = county_sync.sync_county(key)
        except NotImplementedError as exc:
            logger.warning("County %s sync pending: %s", key, exc)
            results[key] = {"status": "not_implemented"}
        except Exception as exc:  # keep going on per-county failure
            logger.exception("County %s sync failed", key)
            results[key] = {"status": "error", "error": str(exc)}
    return results
