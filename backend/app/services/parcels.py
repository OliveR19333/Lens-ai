"""Parcel lookup via PostGIS point-in-polygon (spec §5.3).

Parcels live in per-county spatial tables (``parcels_blount`` etc.) populated by
the monthly GIS sync (spec §5.2). County is part of the table name, so it is
validated against an allow-list before being interpolated — never accept an
arbitrary county string into SQL.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.geocoding import SUPPORTED_COUNTIES

ALLOWED_COUNTIES = set(SUPPORTED_COUNTIES)


class ParcelLookupError(Exception):
    pass


def _table_for(county: str) -> str:
    if county not in ALLOWED_COUNTIES:
        raise ParcelLookupError(f"Unsupported county: {county!r}")
    return f"parcels_{county}"


def lookup_parcel(db: Session, lat: float, lng: float, county: str) -> Optional[dict]:
    """Return the parcel containing (lat, lng), as a dict, or None.

    Implements the spec §5.3 query:
        SELECT parcel_id, owner, address, ST_AsGeoJSON(geom)
        FROM parcels_{county}
        WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
        LIMIT 1;
    """
    table = _table_for(county)
    sql = text(
        f"""
        SELECT parcel_id, owner, address, ST_AsGeoJSON(geom) AS geojson
        FROM {table}
        WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
        LIMIT 1
        """
    )
    row = db.execute(sql, {"lng": lng, "lat": lat}).mappings().first()
    if row is None:
        return None
    import json

    return {
        "parcel_id": row["parcel_id"],
        "owner": row["owner"],
        "address": row["address"],
        "county": county,
        "geojson": json.loads(row["geojson"]) if row["geojson"] else None,
    }
