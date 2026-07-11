"""Parcel-sync trigger + bundle serving (spec §4.2, §5.2)."""
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth import get_current_user
from app.config import Settings, get_settings
from app.gis import bundle
from app.schemas import SyncResponse
from app.services.geocoding import SUPPORTED_COUNTIES
from app.workers import tasks

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/parcels", response_model=SyncResponse)
def trigger_parcel_sync(_user: str = Depends(get_current_user)):
    """`GET /sync/parcels` → manually trigger the county parcel sync (spec §5.2)."""
    task = tasks.sync_all_counties.delay()
    return SyncResponse(triggered=True, task_id=task.id, message="County parcel sync started.")


@router.get("/parcels/manifest")
def parcel_manifest(
    settings: Settings = Depends(get_settings),
    _user: str = Depends(get_current_user),
):
    """`GET /sync/parcels/manifest` → per-county bundle version + size.

    The PWA compares these versions against what it has cached in IndexedDB to
    decide whether to re-download on a WiFi connect (spec §5.2 step 6).
    """
    out = []
    for key, county_name in SUPPORTED_COUNTIES.items():
        b = bundle.read_bundle(key, settings.data_dir)
        out.append(
            {
                "county": key,
                "county_name": county_name,
                "available": b is not None,
                "version_hash": b[1] if b else None,
                "gzip_bytes": len(b[0]) if b else 0,
            }
        )
    return {"counties": out}


@router.get("/parcels/{county}/bundle")
def parcel_bundle(
    county: str,
    settings: Settings = Depends(get_settings),
    _user: str = Depends(get_current_user),
):
    """`GET /sync/parcels/{county}/bundle` → the county GeoJSON bundle.

    Served gzip-compressed; the browser transparently decompresses via
    ``Content-Encoding: gzip`` so the PWA receives plain GeoJSON. The version is
    returned in the ``X-Parcel-Version`` header for cache comparison.
    """
    if county not in SUPPORTED_COUNTIES:
        raise HTTPException(status_code=400, detail=f"Unsupported county: {county!r}")
    b = bundle.read_bundle(county, settings.data_dir)
    if b is None:
        raise HTTPException(
            status_code=404,
            detail=f"No bundle for {county}. Run /sync/parcels first.",
        )
    gz_bytes, version = b
    return Response(
        content=gz_bytes,
        media_type="application/geo+json",
        headers={
            "Content-Encoding": "gzip",
            "X-Parcel-Version": version,
            "Cache-Control": "no-cache",
        },
    )
