"""Import county parcels from a (zipped) shapefile (spec §5).

Reads a shapefile — typically a multi-layer county GIS download zipped up —
auto-detects the **parcels** layer, reprojects to EPSG:4326, normalizes the
attributes to our schema, and packages a PWA bundle (+ optional PostGIS load).

Run on the server via the CLI (it needs geopandas/GDAL, which the backend image
has):

    python -m app.cli importparcels blount /opt/gas-mapping/data/Blount.zip
    python -m app.cli importparcels blount /opt/gas-mapping/data/Blount.zip --list
"""
from __future__ import annotations

import glob
import logging
import os
import tempfile
import zipfile
from dataclasses import dataclass
from typing import List, Optional

from app.gis import bundle, normalize

logger = logging.getLogger("gas.gis.shp")

# Field-name hints that identify a parcels layer (case-insensitive).
PARCEL_HINTS = ["parcel", "parid", "pin", "gpin", "apn", "owner", "cama"]


@dataclass
class LayerInfo:
    name: str
    path: str
    n_features: int
    fields: List[str]
    score: int  # higher = more parcel-like


def _extract(zip_path: str) -> str:
    # Accept a .zip, a directory of shapefiles, or a direct .shp path.
    if os.path.isdir(zip_path):
        return zip_path
    if zip_path.lower().endswith(".zip"):
        dest = tempfile.mkdtemp(prefix="gas_shp_")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest)
        return dest
    return os.path.dirname(zip_path) or "."


def _find_shapefiles(root: str) -> List[str]:
    return sorted(glob.glob(os.path.join(root, "**", "*.shp"), recursive=True))


def _score_layer(fields: List[str], n: int) -> int:
    lf = [f.lower() for f in fields]
    score = sum(2 for hint in PARCEL_HINTS if any(hint in f for f in lf))
    if n > 5000:           # parcels layers are large
        score += 3
    elif n > 500:
        score += 1
    return score


def list_layers(zip_path: str) -> List[LayerInfo]:
    """List every shapefile layer in the archive with a parcel-likeness score."""
    import pyogrio

    root = _extract(zip_path)
    out: List[LayerInfo] = []
    for shp in _find_shapefiles(root):
        try:
            info = pyogrio.read_info(shp)
            fields = list(info.get("fields", []))
            n = int(info.get("features", 0) or 0)
            out.append(
                LayerInfo(
                    name=os.path.splitext(os.path.basename(shp))[0],
                    path=shp,
                    n_features=n,
                    fields=fields,
                    score=_score_layer(fields, n),
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not read %s: %s", shp, exc)
    return sorted(out, key=lambda li: li.score, reverse=True)


def pick_parcels_layer(zip_path: str, layer: Optional[str] = None) -> LayerInfo:
    layers = list_layers(zip_path)
    if not layers:
        raise ValueError("No shapefiles (.shp) found in the archive.")
    if layer:
        for li in layers:
            if li.name.lower() == layer.lower():
                return li
        raise ValueError(f"Layer {layer!r} not found. Available: {[l.name for l in layers]}")
    best = layers[0]
    if best.score <= 0:
        raise ValueError(
            "Couldn't confidently identify a parcels layer. Re-run with --list "
            "and pass --layer <name>."
        )
    return best


def load_feature_collection(layer_path: str, county: str) -> dict:
    """Read a shapefile layer → reproject to 4326 → normalized FeatureCollection."""
    import json

    import geopandas as gpd

    gdf = gpd.read_file(layer_path)
    if gdf.crs is None:
        logger.warning("Layer has no CRS; assuming EPSG:4326.")
    else:
        gdf = gdf.to_crs(epsg=4326)
    # Drop rows without geometry, then emit GeoJSON and normalize attributes.
    gdf = gdf[~gdf.geometry.isna()]
    raw_fc = json.loads(gdf.to_json())
    return normalize.normalize_collection(raw_fc, county)


def import_parcels(county: str, zip_path: str, data_dir: str, layer: Optional[str] = None,
                   load_postgis: bool = True) -> dict:
    """Full import → bundle (+ optional PostGIS). Returns a summary dict."""
    chosen = pick_parcels_layer(zip_path, layer)
    logger.info("Using layer '%s' (%d features) for %s", chosen.name, chosen.n_features, county)
    fc = load_feature_collection(chosen.path, county)
    result = bundle.package_bundle(county, fc, data_dir=data_dir)

    if load_postgis:
        try:
            from sqlalchemy import text

            import geopandas as gpd

            from app.database import engine

            gdf = gpd.GeoDataFrame.from_features(fc["features"], crs="EPSG:4326")
            table = f"parcels_{county}"
            gdf.to_postgis(table, engine, if_exists="replace", index=False)
            with engine.begin() as conn:
                conn.execute(
                    text(f"CREATE INDEX IF NOT EXISTS idx_{table}_geom ON {table} USING GIST (geometry)")
                )
            logger.info("Loaded %d parcels into PostGIS table %s", len(fc["features"]), table)
        except Exception as exc:  # noqa: BLE001
            logger.warning("PostGIS load skipped: %s", exc)

    # Update CountyCache best-effort.
    try:
        import datetime as dt

        from app.database import SessionLocal
        from app.models import CountyCache, County

        db = SessionLocal()
        try:
            row = db.get(CountyCache, County(county))
            if row is None:
                row = CountyCache(county=County(county))
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
        logger.info("CountyCache update skipped: %s", exc)

    return {
        "county": county,
        "layer": chosen.name,
        "parcels": result.parcel_count,
        "bundle_kb": result.gzip_bytes // 1024,
        "version": result.version_hash,
    }
