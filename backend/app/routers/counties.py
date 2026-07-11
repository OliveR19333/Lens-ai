"""County listing + cache status (spec §4.2, §5.1)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import CountyCache
from app.schemas import CountyStatus

router = APIRouter(prefix="/counties", tags=["counties"])

# Static portal metadata (spec §5.1). Sync state is merged in from the DB.
COUNTY_PORTALS = {
    "blount": ("Blount County", "https://www.blounttn.org/2153/GIS-Mapping"),
    "knox": ("Knox County", "https://www.knoxplanning.org/gis/"),
    "sevier": ("Sevier County", "https://www.seviercountytn.org/gis/"),
    "loudon": ("Loudon County", "https://loudoncounty-tn.gov/"),
    "monroe": ("Monroe County", "https://monroegovtn.org/"),
}


@router.get("", response_model=list[CountyStatus])
def list_counties(
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`GET /counties` → supported counties + cache status."""
    cache = {c.county.value: c for c in db.query(CountyCache).all()}
    out: list[CountyStatus] = []
    for key, (name, url) in COUNTY_PORTALS.items():
        c = cache.get(key)
        out.append(
            CountyStatus(
                county=key,
                county_name=name,
                gis_portal_url=url,
                version_hash=c.version_hash if c else None,
                parcel_count=c.parcel_count if c else 0,
                bundle_size_bytes=c.bundle_size_bytes if c else 0,
                last_synced_at=c.last_synced_at if c else None,
            )
        )
    return out
