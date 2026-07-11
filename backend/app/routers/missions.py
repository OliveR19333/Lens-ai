"""Mission generation + KMZ download (spec §4.2, §6)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Project, ProjectStatus
from app.schemas import MissionGenerateRequest, MissionGenerateResponse
from app.services.mission import MissionParams, build_mission_kmz
from app.storage import kmz_path, save_kmz

router = APIRouter(tags=["mission"])


@router.post("/mission/generate", response_model=MissionGenerateResponse)
def generate_mission(
    body: MissionGenerateRequest,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /mission/generate` → parcel GeoJSON → Waypoint KMZ file."""
    params = MissionParams(
        altitude_ft=body.altitude_ft,
        forward_overlap=body.forward_overlap,
        side_overlap=body.side_overlap,
        buffer_ft=body.buffer_ft,
    )
    try:
        result = build_mission_kmz(body.parcel_geojson, params)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    mission_id = str(uuid.uuid4())
    path = save_kmz(mission_id, result.kmz_bytes)

    # If tied to a project, advance it to mission_ready and record the KMZ path.
    if body.project_id:
        project = db.get(Project, body.project_id)
        if project:
            project.mission_kmz = str(path)
            project.status = ProjectStatus.mission_ready
            db.commit()

    return MissionGenerateResponse(
        mission_id=mission_id,
        summary=result.summary(),
        kmz_url=f"/mission/{mission_id}/kmz",
    )


@router.get("/mission/{mission_id}/kmz")
def download_kmz(mission_id: str, _user: str = Depends(get_current_user)):
    """`GET /mission/{id}/kmz` → download the generated KMZ file."""
    path = kmz_path(mission_id)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KMZ not found")
    return FileResponse(
        path,
        media_type="application/vnd.google-earth.kmz",
        filename=f"mission-{mission_id}.kmz",
    )
