"""Per-county GeoJSON bundle packaging for PWA offline sync (spec §5.2 step 5-6).

Takes a normalized FeatureCollection and produces a gzip-compressed bundle the
PWA downloads into IndexedDB, plus a stable version hash so the app can detect a
new version on WiFi connect. Pure standard library — unit-tested.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BundleResult:
    county: str
    version_hash: str
    parcel_count: int
    raw_bytes: int
    gzip_bytes: int
    path: Path | None = None

    def as_dict(self) -> dict:
        return {
            "county": self.county,
            "version_hash": self.version_hash,
            "parcel_count": self.parcel_count,
            "raw_bytes": self.raw_bytes,
            "gzip_bytes": self.gzip_bytes,
            "path": str(self.path) if self.path else None,
        }


def _canonical_json(fc: dict) -> bytes:
    """Deterministic JSON encoding so the version hash is stable across runs."""
    return json.dumps(fc, sort_keys=True, separators=(",", ":")).encode("utf-8")


def version_hash(fc: dict) -> str:
    return hashlib.sha256(_canonical_json(fc)).hexdigest()[:16]


def package_bundle(county: str, fc: dict, data_dir: str | Path | None = None) -> BundleResult:
    """Compress a county FeatureCollection and (optionally) write it to disk."""
    raw = _canonical_json(fc)
    gz = gzip.compress(raw, compresslevel=9)
    result = BundleResult(
        county=county,
        version_hash=hashlib.sha256(raw).hexdigest()[:16],
        parcel_count=len(fc.get("features", [])),
        raw_bytes=len(raw),
        gzip_bytes=len(gz),
    )
    if data_dir is not None:
        out_dir = Path(data_dir) / "parcels"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{county}.geojson.gz"
        path.write_bytes(gz)
        # Sidecar with the version so the bundle endpoint can serve it cheaply.
        (out_dir / f"{county}.version").write_text(result.version_hash)
        result.path = path
    return result


def read_bundle(county: str, data_dir: str | Path) -> tuple[bytes, str] | None:
    """Return (gzip_bytes, version_hash) for a packaged county, or None."""
    out_dir = Path(data_dir) / "parcels"
    gz_path = out_dir / f"{county}.geojson.gz"
    ver_path = out_dir / f"{county}.version"
    if not gz_path.exists():
        return None
    version = ver_path.read_text().strip() if ver_path.exists() else ""
    return gz_path.read_bytes(), version
