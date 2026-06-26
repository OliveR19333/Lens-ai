"""Manual annotation layer helpers (spec §12 — user annotation layer).

Pure standard library. Operators mark features by hand on the map; those are
stored separately from the AI-detected ``features_geojson`` (so re-running
detection never clobbers manual edits) and merged at render time.
"""
from __future__ import annotations

import uuid
from typing import Optional

VALID_TYPES = {"pond", "trees", "structure", "driveway", "fence", "slope", "note"}


def empty_collection() -> dict:
    return {"type": "FeatureCollection", "features": []}


def make_annotation(feature_type: str, geometry: dict, label: str = "", notes: str = "") -> dict:
    """Build one manual annotation feature (spec §11.2 shape + source=manual)."""
    ft = feature_type if feature_type in VALID_TYPES else "note"
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "id": str(uuid.uuid4()),
            "feature_type": ft,
            "label": label or ft.capitalize(),
            "confidence": 1.0,
            "source": "manual",
            "notes": notes,
        },
    }


def append_annotation(annotations: Optional[dict], feature: dict) -> dict:
    """Append a feature to an annotations FeatureCollection (creating it if None)."""
    fc = annotations or empty_collection()
    feats = list(fc.get("features", []))
    feats.append(feature)
    return {"type": "FeatureCollection", "features": feats}


def remove_annotation(annotations: Optional[dict], annotation_id: str) -> dict:
    fc = annotations or empty_collection()
    feats = [f for f in fc.get("features", []) if (f.get("properties") or {}).get("id") != annotation_id]
    return {"type": "FeatureCollection", "features": feats}


def merge_features(detected: Optional[dict], annotations: Optional[dict]) -> dict:
    """Combine AI-detected features + manual annotations for rendering (spec §9)."""
    feats = []
    if detected:
        feats.extend(detected.get("features", []))
    if annotations:
        feats.extend(annotations.get("features", []))
    return {"type": "FeatureCollection", "features": feats}
