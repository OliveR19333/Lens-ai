"""Project lifecycle + processing endpoints (spec §4.2, §7, §8, §9)."""
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import County, Project, ProjectStatus, UseCase
from app.schemas import (
    AnnotationCreateRequest,
    AnnotationsResponse,
    MapsResponse,
    ProjectCreateRequest,
    ProjectListItem,
    ProjectResponse,
    ProjectStatusResponse,
)
from app.services import annotations as ann
from app.services import feature_detection, webodm
from app.workers import tasks

router = APIRouter(prefix="/project", tags=["project"])


@router.post("/create", response_model=ProjectResponse)
def create_project(
    body: ProjectCreateRequest,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
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
        owner_username=user,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/list", response_model=list[ProjectListItem])
def list_projects(
    include_archived: bool = False,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /project/list` → project history, newest first (spec §12)."""
    q = db.query(Project)
    if not include_archived:
        q = q.filter(Project.archived.is_(False))
    projects = q.order_by(Project.created_at.desc()).all()
    return [ProjectListItem.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /project/{id}` → full project detail."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/archive", response_model=ProjectListItem)
def archive_project(
    project_id: str,
    archived: bool = True,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/{id}/archive?archived=true|false` → (un)archive (spec §12)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.archived = archived
    db.commit()
    db.refresh(project)
    return ProjectListItem.model_validate(project)


@router.get("/{project_id}/annotations", response_model=AnnotationsResponse)
def get_annotations(
    project_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /project/{id}/annotations` → manual annotation layer (spec §12)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return AnnotationsResponse(
        id=project_id, annotations=project.annotations_geojson or ann.empty_collection()
    )


@router.post("/{project_id}/annotations", response_model=AnnotationsResponse)
def add_annotation(
    project_id: str,
    body: AnnotationCreateRequest,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/{id}/annotations` → append a manual feature (spec §12)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    feature = ann.make_annotation(body.feature_type, body.geometry, body.label, body.notes)
    project.annotations_geojson = ann.append_annotation(project.annotations_geojson, feature)
    db.commit()
    return AnnotationsResponse(id=project_id, annotations=project.annotations_geojson)


@router.delete("/{project_id}/annotations/{annotation_id}", response_model=AnnotationsResponse)
def delete_annotation(
    project_id: str,
    annotation_id: str,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`DELETE /project/{id}/annotations/{ann_id}` → remove one annotation."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.annotations_geojson = ann.remove_annotation(project.annotations_geojson, annotation_id)
    db.commit()
    return AnnotationsResponse(id=project_id, annotations=project.annotations_geojson)


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


@router.post("/{project_id}/upload-video", response_model=ProjectStatusResponse)
async def upload_video(
    project_id: str,
    video: UploadFile = File(...),
    fps: float = Form(1.0),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /project/{id}/upload-video` → upload a flight video; the server
    extracts frames at ``fps`` and feeds them to WebODM like an image set.

    Recording continuous video guarantees coverage with no gaps from a missed
    interval shot — the pilot just flies the passes with the camera rolling.
    """
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        saved = await webodm.stage_video_frames(project_id, video, fps=fps)
    except webodm.WebODMError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    task = tasks.process_webodm_job.delay(project_id, saved)
    project.status = ProjectStatus.processing
    db.commit()
    return ProjectStatusResponse(
        id=project_id,
        status=project.status.value,
        webodm_task_id=task.id,
        message=f"Extracted {len(saved)} frames from video; queued for WebODM processing.",
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
