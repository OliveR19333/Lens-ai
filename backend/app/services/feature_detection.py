"""AI feature detection — public entry point (spec §8).

Delegates to the ``detection`` package (tiling → YOLOv8 → merge/NMS →
georeference → spectral water → slope). Kept as a thin module so existing
imports (``app.services.feature_detection``) and the Celery task stay stable.
"""
from __future__ import annotations

from typing import Optional

from app.services.detection import detect_features as _detect_features
from app.services.detection.pipeline import empty_feature_collection  # noqa: F401

FEATURE_CLASSES = ["pond", "trees", "structure", "driveway", "fence", "slope"]


def detect_features(
    ortho_tif: str,
    dtm_tif: Optional[str] = None,
    *,
    model_path: Optional[str] = None,
    min_confidence: Optional[float] = None,
) -> dict:
    """Run the detection pipeline → GeoJSON FeatureCollection (spec §11.2)."""
    return _detect_features(
        ortho_tif, dtm_tif, model_path=model_path, min_confidence=min_confidence
    )
