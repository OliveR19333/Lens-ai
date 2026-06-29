"""Normalize raw county parcel attributes to our schema (spec §5, §11.2).

County GIS layers use wildly different field names for the same things
(``PARCELID`` vs ``PIN`` vs ``Parcel``; ``OWNER`` vs ``OwnerName``; ...). This
maps each feature's properties onto a stable, small set the app relies on, while
keeping the geometry untouched. Pure stdlib — unit-tested.
"""
from __future__ import annotations

from typing import Optional

# Candidate source field names, in priority order, per target field.
FIELD_ALIASES = {
    "parcel_id": ["parcel_id", "PARCELID", "PARCEL_ID", "PIN", "PARID", "Parcel",
                  "GPIN", "APN", "GISLINK", "GISLINK2", "PARCELNUMB", "PARCEL_NUM"],
    "owner": ["owner", "OWNER", "OWNERNAME", "OwnerName", "OWNER_NAME", "Owner1", "DEEDED_OWN"],
    "address": [
        "address", "ADDRESS", "SITEADDR", "SITE_ADDR", "PropAddr", "PROP_ADDR",
        "PAR_ADDR", "ADDR", "SITUS", "SITUS_ADDR", "LOCATION",
    ],
}


def _first_present(props: dict, keys: list[str]) -> Optional[str]:
    # Case-insensitive lookup across the candidate keys.
    lowered = {k.lower(): v for k, v in props.items()}
    for key in keys:
        if key in props and props[key] not in (None, ""):
            return str(props[key])
        lk = key.lower()
        if lk in lowered and lowered[lk] not in (None, ""):
            return str(lowered[lk])
    return None


def normalize_feature(feature: dict, county: str) -> dict:
    """Return a feature with normalized ``properties`` and original geometry."""
    props = feature.get("properties") or {}
    normalized = {
        "parcel_id": _first_present(props, FIELD_ALIASES["parcel_id"]),
        "owner": _first_present(props, FIELD_ALIASES["owner"]),
        "address": _first_present(props, FIELD_ALIASES["address"]),
        "county": county,
    }
    return {
        "type": "Feature",
        "geometry": feature.get("geometry"),
        "properties": normalized,
    }


def normalize_collection(fc: dict, county: str) -> dict:
    """Normalize every feature in a FeatureCollection, dropping geometry-less ones."""
    out = []
    for f in fc.get("features", []):
        if not f.get("geometry"):
            continue
        out.append(normalize_feature(f, county))
    return {"type": "FeatureCollection", "features": out}
