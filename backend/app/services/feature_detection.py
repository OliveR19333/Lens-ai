"""AI feature detection over the orthomosaic (spec §8).

⚙ STUB — Phase 3. The pipeline shape and output schema (spec §8 / §11.2) are
fixed here so the rest of the system can be wired against them; the heavy
ultralytics / rasterio / numpy work is left as TODO.

Target classes (spec §8.2): pond, trees, structure, driveway, fence, slope.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from app.config import get_settings

logger = logging.getLogger("gas.features")

FEATURE_CLASSES = ["pond", "trees", "structure", "driveway", "fence", "slope"]


def empty_feature_collection() -> dict:
    return {"type": "FeatureCollection", "features": []}


def make_feature(feature_type: str, geometry: dict, confidence: float, area_sqft: float) -> dict:
    """Build one feature matching the spec §11.2 schema."""
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "feature_type": feature_type,
            "label": feature_type.capitalize(),
            "confidence": round(confidence, 2),
            "area_sqft": round(area_sqft, 1),
            "notes": "",
        },
    }


def detect_features(ortho_tif: str, dtm_tif: str | None = None) -> dict:
    """Run YOLOv8 + spectral water + slope analysis → GeoJSON FeatureCollection.

    ⚙ TODO (spec §8.3):
        chips = tile_geotiff(ortho_tif, size=640, overlap=64)
        model = YOLO(settings.yolo_model_path)
        detections = [model(chip) for chip in chips]
        features = merge_detections_to_geojson(detections, ortho_transform)
        features += detect_water_spectral(ortho_tif)      # HSV blue clustering
        features += slope_to_arrows(*compute_slope_aspect(dtm_tif), spacing=50)
        filter by settings.feature_min_confidence (0.45)
    """
    settings = get_settings()
    logger.info(
        "Feature detection requested for %s (model=%s, min_conf=%.2f) — STUB",
        ortho_tif,
        settings.yolo_model_path,
        settings.feature_min_confidence,
    )
    if not Path(ortho_tif).exists():
        raise FileNotFoundError(ortho_tif)
    # Returns an empty (but valid) collection until the model is wired in.
    return empty_feature_collection()


def detect_water_spectral(ortho_tif: str) -> List[dict]:
    """Spectral (HSV blue range) water-body detection (spec §8.3). TODO."""
    raise NotImplementedError("Spectral water detection not implemented (spec §8.3).")


def compute_slope_aspect(dtm_tif: str):
    """rasterio gradient on DTM → (slope, aspect) rasters (spec §8.3). TODO."""
    raise NotImplementedError("Slope/aspect computation not implemented (spec §8.3).")
