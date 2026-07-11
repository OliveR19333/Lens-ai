"""Geocoding endpoint (spec §4.2, §4.3)."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.config import Settings, get_settings
from app.schemas import GeocodeRequest, GeocodeResponse
from app.services.geocoding import GeocodeError, geocode

router = APIRouter(prefix="/geocode", tags=["geocode"])


@router.post("", response_model=GeocodeResponse)
def geocode_address(
    body: GeocodeRequest,
    settings: Settings = Depends(get_settings),
    _user: str = Depends(get_current_user),
):
    """`POST /geocode` → address → lat/lng + county detection."""
    try:
        result = geocode(
            body.address,
            census_benchmark=settings.census_benchmark,
            google_api_key=settings.google_maps_api_key,
        )
    except GeocodeError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return GeocodeResponse(**result.as_dict())
