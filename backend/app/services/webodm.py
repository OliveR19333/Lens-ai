"""WebODM REST client (spec §7).

⚙ STUB — Phase 2. The call sequence (spec §7.2) is laid out with real endpoint
paths and payloads; network calls are guarded so importing this module never
requires a running WebODM. Fill in the `httpx` calls and wire credentials from
settings when the WebODM Docker instance is available.

Pipeline (spec §7.2):
    1. POST /api/token-auth/                 → token
    2. POST /api/projects/                   → project id
    3. POST /api/projects/{id}/tasks/        → task uuid  (images[] + options)
    4. GET  /api/projects/{id}/tasks/{uuid}/ → status (40 = COMPLETED)
    5. GET  .../download/{orthophoto,dsm,dtm}.tif
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from app.config import get_settings
from app.storage import project_dir

logger = logging.getLogger("gas.webodm")

# WebODM task status codes (subset).
STATUS_QUEUED = 10
STATUS_RUNNING = 20
STATUS_FAILED = 30
STATUS_COMPLETED = 40
STATUS_CANCELED = 50

PROCESSING_OPTIONS = [
    {"name": "dsm", "value": True},
    {"name": "dtm", "value": True},
    {"name": "orthophoto-resolution", "value": 2},
]


async def stage_uploads(project_id: str, images) -> List[str]:
    """Persist uploaded images to the project's storage dir; return their paths.

    Accepts FastAPI ``UploadFile`` objects. Kept dependency-light so the upload
    endpoint works even before the WebODM submission path is implemented.
    """
    dest = project_dir(project_id) / "images"
    dest.mkdir(parents=True, exist_ok=True)
    saved: List[str] = []
    for img in images:
        out = dest / Path(img.filename).name
        data = await img.read()
        out.write_bytes(data)
        saved.append(str(out))
    logger.info("Staged %d images for project %s", len(saved), project_id)
    return saved


def authenticate() -> str:
    """POST /api/token-auth/ → token. TODO: implement with httpx."""
    settings = get_settings()
    raise NotImplementedError(
        "WebODM auth not implemented. POST "
        f"{settings.webodm_base_url}/token-auth/ with username/password."
    )


def create_project(name: str) -> int:
    """POST /api/projects/ → project id. TODO."""
    raise NotImplementedError("WebODM create_project not implemented (spec §7.2 step 2).")


def submit_task(webodm_project_id: int, image_paths: List[str]) -> str:
    """POST /api/projects/{id}/tasks/ with images + PROCESSING_OPTIONS → task uuid. TODO."""
    raise NotImplementedError("WebODM submit_task not implemented (spec §7.2 step 3).")


def get_task_status(webodm_project_id: int, task_uuid: str) -> str:
    """GET task status; map the numeric code to a human label. TODO: real call."""
    # Placeholder mapping so the status endpoint returns something coherent.
    return "unknown"


def download_outputs(webodm_project_id: int, task_uuid: str, dest_dir: Path) -> dict:
    """Download orthophoto.tif / dsm.tif / dtm.tif (spec §7.2 step 5). TODO."""
    raise NotImplementedError("WebODM download_outputs not implemented (spec §7.3).")
