"""Parcel lookup endpoint (spec §4.2, §5.3)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.schemas import ParcelLookupRequest, ParcelResponse
from app.services.geocoding import SUPPORTED_COUNTIES
from app.services.parcels import ParcelLookupError, lookup_parcel

router = APIRouter(prefix="/parcel", tags=["parcel"])


@router.post("/lookup", response_model=ParcelResponse)
def parcel_lookup(
    body: ParcelLookupRequest,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /parcel/lookup` → lat/lng → parcel boundary GeoJSON.

    If ``county`` is not supplied, every supported county is searched (the point
    falls in at most one). Requires the monthly GIS sync (spec §5.2) to have
    populated the per-county spatial tables.
    """
    counties = [body.county] if body.county else list(SUPPORTED_COUNTIES)
    try:
        for county in counties:
            parcel = lookup_parcel(db, body.lat, body.lng, county)
            if parcel:
                return ParcelResponse(**parcel)
    except ParcelLookupError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No parcel found at this location in the supported counties.",
    )
