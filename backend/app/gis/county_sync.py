"""County GIS download → PostGIS → PWA bundle (spec §5.2).

⚙ STUB — Phase 1/4. The per-county portal metadata and the sync steps are laid
out; the shapefile download + ``pyogrio``/``geopandas`` conversion + PostGIS
load + bundle packaging are left as TODO.

> ⚑ NOTE (spec §5.1): each county GIS portal must be manually verified at build
> time. Some require free account registration for bulk shapefile download.
> Confirm current download URLs and formats before implementation.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("gas.gis.sync")


@dataclass
class CountySource:
    key: str
    name: str
    portal_url: str
    export_format: str
    # Direct bulk-download URL — TODO: verify per spec §5.1 before use.
    download_url: str | None = None


COUNTY_SOURCES = {
    "blount": CountySource(
        "blount", "Blount County, TN",
        "https://www.blounttn.org/2153/GIS-Mapping", "Shapefile / KML",
    ),
    "knox": CountySource(
        "knox", "Knox County, TN",
        "https://www.knoxplanning.org/gis/", "Shapefile / GeoJSON",
    ),
    "sevier": CountySource(
        "sevier", "Sevier County, TN",
        "https://www.seviercountytn.org/gis/", "Shapefile / KML",
    ),
}


def file_version_hash(path: Path) -> str:
    """Stable content hash used to tell the PWA when a bundle changed (spec §5.2)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def sync_county(county_key: str) -> dict:
    """Download, convert, load, and package one county's parcels (spec §5.2).

    ⚙ TODO:
        1. download latest shapefile/GeoJSON from source.download_url
        2. convert shapefile → GeoJSON via pyogrio/geopandas if needed
        3. load into PostGIS table parcels_{county} (EPSG:4326)
        4. package compressed per-county GeoJSON bundle (~10–30MB) for the PWA
        5. compute version hash + update CountyCache row
    """
    source = COUNTY_SOURCES.get(county_key)
    if not source:
        raise ValueError(f"Unknown county: {county_key!r}")
    logger.info("sync_county(%s) STUB — portal %s", county_key, source.portal_url)
    raise NotImplementedError(
        f"County sync for {source.name} not implemented (spec §5.2). "
        "Verify the bulk download URL/format first (spec §5.1)."
    )
