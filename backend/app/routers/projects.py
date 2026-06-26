"""Project lifecycle + processing endpoints (spec §4.2, §7, §8, §9)."""
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import County, Project, ProjectStatus, UseCase
from app.schemas import (
    MapsResponse,
    ProjectCreateRequest,
    ProjectResponse,
    ProjectStatusResponse,
)
from app.services import feature_detection, webodm
from app.workers import tasks

router = APIRouter(prefix="/project", tags=["project"])


@router.post("/create", response_model=ProjectResponse)
def create_project(
    body: ProjectCreateRequest,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/create` → create a new mapping project."""
    project = Project(
        address=body.address,
        county=County(body.county) if body.county else None,
        lat=body.lat,
        lng=body.lng,
        parcel_id=body.parcel_id,
        parcel_geojson=body.parcel_geojson,
        use_case=UseCase(body.use_case),
        notes=body.notes,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/upload", response_model=ProjectStatusResponse)
async def upload_images(
    project_id: str,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/{id}/upload` → upload drone images to WebODM (spec §7.2)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Persist uploads, then hand off to a Celery task that drives WebODM.
    saved = await webodm.stage_uploads(project_id, images)
    task = tasks.process_webodm_job.delay(project_id, saved)
    project.status = ProjectStatus.processing
    db.commit()
    return ProjectStatusResponse(
        id=project_id,
        status=project.status.value,
        webodm_task_id=task.id,
        message=f"Queued {len(saved)} images for WebODM processing.",
    )


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
def project_status(
    project_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /project/{id}/status` → WebODM processing status (spec §7.2)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    webodm_status = None
    if project.webodm_project_id and project.webodm_task_id:
        webodm_status = webodm.get_task_status(
            project.webodm_project_id, project.webodm_task_id
        )
    return ProjectStatusResponse(
        id=project_id,
        status=project.status.value,
        webodm_task_id=project.webodm_task_id,
        webodm_status=webodm_status,
    )


@router.post("/{project_id}/features", response_model=ProjectStatusResponse)
def trigger_features(
    project_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/{id}/features` → trigger AI feature detection (spec §8)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.ortho_tif:
        raise HTTPException(
            status_code=409, detail="Orthomosaic not ready; run processing first."
        )
    task = tasks.detect_features.delay(project_id)
    return ProjectStatusResponse(
        id=project_id,
        status=project.status.value,
        webodm_task_id=task.id,
        message="Feature detection queued.",
    )


@router.post("/{project_id}/maps/render", response_model=ProjectStatusResponse)
def render_project_maps(
    project_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/{id}/maps/render` → queue Map 1 + Map 2 rendering (spec §9).

    Works with just the parcel boundary (renders scaled grid sheets); richer
    output appears once WebODM ortho/DEM and AI features are attached.
    """
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.parcel_geojson:
        raise HTTPException(status_code=409, detail="Project has no parcel boundary.")
    task = tasks.render_maps.delay(project_id)
    return ProjectStatusResponse(
        id=project_id, status=project.status.value, webodm_task_id=task.id,
        message="Map rendering queued.",
    )


@router.get("/{project_id}/maps", response_model=MapsResponse)
def project_maps(
    project_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /project/{id}/maps` → flat + elevation map PDFs (spec §9)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    ready = bool(project.map_flat_pdf and project.map_elev_pdf)
    return MapsResponse(
        id=project_id,
        map_flat_pdf_url=f"/project/{project_id}/maps/flat.pdf" if project.map_flat_pdf else None,
        map_elev_pdf_url=f"/project/{project_id}/maps/elev.pdf" if project.map_elev_pdf else None,
        print_scale=project.print_scale,
        ready=ready,
    )


@router.get("/{project_id}/maps/{kind}.pdf")
def download_map_pdf(
    project_id: str,
    kind: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /project/{id}/maps/{flat|elev}.pdf` → the rendered PDF (spec §9)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    path = {"flat": project.map_flat_pdf, "elev": project.map_elev_pdf}.get(kind)
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail=f"{kind} map not rendered yet.")
    return FileResponse(path, media_type="application/pdf", filename=f"{kind}-map-{project_id}.pdf")
