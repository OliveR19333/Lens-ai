"""Manual parcel-sync trigger (spec §4.2, §5.2)."""
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.schemas import SyncResponse
from app.workers import tasks

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/parcels", response_model=SyncResponse)
def trigger_parcel_sync(_user: str = Depends(get_current_user)):
    """`GET /sync/parcels` → manually trigger the county parcel sync.

    Runs the same job the Celery beat schedule fires monthly (spec §5.2).
    """
    task = tasks.sync_all_counties.delay()
    return SyncResponse(
        triggered=True,
        task_id=task.id,
        message="County parcel sync started.",
    )
