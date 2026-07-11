"""County GIS sync orchestration (spec §5.2).

Pipeline per county:
  1. download the parcel layer from its ArcGIS REST service (paginated GeoJSON)
  2. normalize attributes to our parcel schema
  3. package a gzip bundle for the PWA + compute a version hash
  4. (optional) load into PostGIS for server-side point-in-polygon lookup
  5. update the CountyCache row

Steps 1-3 + 5 are fully implemented and dependency-light. Step 4 (PostGIS load)
is optional and only runs when geopandas + a database are available; the PWA
bundle is the field-facing artifact and does not require it.

> ⚑ NOTE (spec §5.1): the per-county service URLs below MUST be verified at
> build time — some portals change endpoints or require registration. Each is
> marked `verified=False` until confirmed against the live portal.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.gis import arcgis, bundle, normalize

logger = logging.getLogger("gas.gis.sync")


@dataclass
class CountySource:
    key: str
    name: str
    portal_url: str
    export_format: str
    # ArcGIS REST FeatureServer/MapServer parcel layer query endpoint.
    service_url: Optional[str] = None
    # Optional server-side filter (e.g. county name on a statewide layer).
    where_clause: str = "1=1"
    verified: bool = False
    source_note: str = ""


# Recommended authoritative source: the Tennessee Comptroller statewide parcel
# dataset, served via TNMap (STS GIS). It covers all 95 counties, updates
# monthly around the 1st business day (matches our sync cadence, spec §5.2), and
# is explicitly published for public/government download — unlike some county
# servers (e.g. Blount/KCS) whose terms PROHIBIT bulk/automated retrieval.
#
#   Portal:    https://tn-tnmap.opendata.arcgis.com/   (download by county)
#   REST root: https://tnmap.tn.gov/arcgis/rest/services/
#   Comptroller: https://comptroller.tn.gov/office-functions/pa/gisredistricting/
#                redistricting-and-land-use-maps/parcel-data.html
#
# ⚑ NOTE: the exact statewide parcels layer path + county field name still need
# to be confirmed against the live REST directory (the build sandbox could not
# reach these hosts). Set `service_url` + `where_clause` below once confirmed,
# then flip `verified=True`. See docs/GIS_DATA_SOURCES.md for the full findings.
STATEWIDE_PARCELS_REST_ROOT = "https://tnmap.tn.gov/arcgis/rest/services/"

COUNTY_SOURCES = {
    "blount": CountySource(
        "blount", "Blount County, TN",
        "https://tn-tnmap.opendata.arcgis.com/", "Shapefile / GeoJSON",
        service_url=None,                 # statewide layer URL — confirm (see note)
        where_clause="UPPER(CONAME)='BLOUNT'",
        verified=False,
        source_note=(
            "Prefer the TN statewide Comptroller layer. The Blount/KCS county "
            "server prohibits automated bulk retrieval."
        ),
    ),
    "knox": CountySource(
        "knox", "Knox County, TN",
        "https://www.knoxplanning.org/gis/", "Shapefile / GeoJSON",
        # Knox/KGIS publishes parcels via ArcGIS REST at
        # https://www.kgis.org/gisserver/rest/services/ — confirm the parcels
        # MapServer/FeatureServer layer id. Statewide layer also covers Knox.
        service_url=None,
        where_clause="UPPER(CONAME)='KNOX'",
        verified=False,
        source_note="KGIS ArcGIS REST, or the TN statewide layer filtered to Knox.",
    ),
    "sevier": CountySource(
        "sevier", "Sevier County, TN",
        "https://tn-tnmap.opendata.arcgis.com/", "Shapefile / GeoJSON",
        service_url=None,
        where_clause="UPPER(CONAME)='SEVIER'",
        verified=False,
        source_note="Use the TN statewide Comptroller layer filtered to Sevier.",
    ),
}


@dataclass
class SyncOutcome:
    county: str
    status: str  # "synced" | "no_source" | "error"
    parcel_count: int = 0
    version_hash: Optional[str] = None
    gzip_bytes: int = 0
    error: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "county": self.county,
            "status": self.status,
            "parcel_count": self.parcel_count,
            "version_hash": self.version_hash,
            "gzip_bytes": self.gzip_bytes,
            "error": self.error,
        }


def sync_county(county_key: str, *, fetch=arcgis._default_fetch) -> SyncOutcome:
    """Run the full sync for one county. ``fetch`` is injectable for testing."""
    source = COUNTY_SOURCES.get(county_key)
    if not source:
        raise ValueError(f"Unknown county: {county_key!r}")

    if not source.service_url:
        logger.warning(
            "County %s has no verified GIS service URL yet (spec §5.1) — "
            "skipping automated download. Use Settings → Import in the PWA, "
            "or set COUNTY_SOURCES['%s'].service_url.",
            county_key, county_key,
        )
        return SyncOutcome(county=county_key, status="no_source")

    settings = get_settings()
    try:
        raw_fc = arcgis.fetch_layer_geojson(
            source.service_url, where=source.where_clause, fetch=fetch
        )
        norm_fc = normalize.normalize_collection(raw_fc, county_key)
        result = bundle.package_bundle(county_key, norm_fc, data_dir=settings.data_dir)

        # Optional PostGIS load for server-side parcel lookup.
        try:
            _load_postgis(county_key, norm_fc)
        except Exception as exc:  # noqa: BLE001 — PostGIS is optional here
            logger.info("PostGIS load skipped for %s: %s", county_key, exc)

        _update_county_cache(county_key, result)
        logger.info(
            "Synced %s: %d parcels, %d KB gzip (v%s)",
            county_key, result.parcel_count, result.gzip_bytes // 1024, result.version_hash,
        )
        return SyncOutcome(
            county=county_key,
            status="synced",
            parcel_count=result.parcel_count,
            version_hash=result.version_hash,
            gzip_bytes=result.gzip_bytes,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Sync failed for %s", county_key)
        return SyncOutcome(county=county_key, status="error", error=str(exc))


def _load_postgis(county_key: str, fc: dict) -> None:
    """Load parcels into the per-county PostGIS table (spec §5.3). Optional."""
    import geopandas as gpd  # heavy import, kept local
    from sqlalchemy import text

    from app.database import engine

    gdf = gpd.GeoDataFrame.from_features(fc["features"], crs="EPSG:4326")
    table = f"parcels_{county_key}"
    gdf.to_postgis(table, engine, if_exists="replace", index=False)
    with engine.begin() as conn:
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_geom ON {table} USING GIST (geometry)"))


def _update_county_cache(county_key: str, result: "bundle.BundleResult") -> None:
    """Upsert the CountyCache row (best-effort; skipped if DB unavailable)."""
    import datetime as dt

    try:
        from app.database import SessionLocal
        from app.models import CountyCache, County

        db = SessionLocal()
        try:
            row = db.get(CountyCache, County(county_key))
            if row is None:
                row = CountyCache(county=County(county_key))
                db.add(row)
            row.version_hash = result.version_hash
            row.parcel_count = result.parcel_count
            row.bundle_path = str(result.path) if result.path else None
            row.bundle_size_bytes = result.gzip_bytes
            row.last_synced_at = dt.datetime.now(dt.timezone.utc)
            db.commit()
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001
        logger.info("CountyCache update skipped for %s: %s", county_key, exc)


def file_version_hash(path: Path) -> str:
    """Stable content hash of a file (kept for compatibility / external bundles)."""
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]
