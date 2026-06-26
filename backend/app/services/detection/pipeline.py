"""Feature-detection orchestration (spec §8.3).

Ties the pure stages together and adds the lazily-imported heavy work:

  1. tile the orthomosaic GeoTIFF (640×640, 64 px overlap)
  2. run YOLOv8 on each chip (ultralytics) → detections in global pixels
  3. merge / NMS / confidence-filter / georeference → GeoJSON features
  4. spectral water detection over the full ortho (HSV blue clustering)
  5. slope arrows from the DTM

Every heavy dependency (rasterio, ultralytics) is imported lazily and guarded,
so a missing model or GDAL degrades gracefully (e.g. water+slope still run, or
an empty—but valid—FeatureCollection is returned) instead of crashing the job.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from app.services.detection import merge, spectral
from app.services.detection.merge import Detection
from app.services.detection.tiling import generate_tiles

logger = logging.getLogger("gas.detection")

FEATURE_CLASSES = ["pond", "trees", "structure", "driveway", "fence", "slope"]


def empty_feature_collection() -> dict:
    return {"type": "FeatureCollection", "features": []}


def _affine6(transform) -> tuple:
    """rasterio Affine → our 6-tuple (a, b, c, d, e, f)."""
    return (transform.a, transform.b, transform.c, transform.d, transform.e, transform.f)


def _run_yolo(ortho_path: str, model_path: str, transform, min_confidence: float) -> List[dict]:
    try:
        import numpy as np
        import rasterio
        from ultralytics import YOLO
    except Exception as exc:  # noqa: BLE001
        logger.info("YOLO/rasterio unavailable (%s) — skipping object detection.", exc)
        return []
    if not Path(model_path).exists():
        logger.warning("YOLO model not found at %s — skipping object detection.", model_path)
        return []

    model = YOLO(model_path)
    names = model.names
    detections: List[Detection] = []
    with rasterio.open(ortho_path) as src:
        tiles = generate_tiles(src.width, src.height, size=640, overlap=64)
        for t in tiles:
            window = rasterio.windows.Window(t.col_off, t.row_off, t.width, t.height)
            chip = src.read(window=window, indexes=[1, 2, 3], out_dtype="uint8")
            img = np.transpose(chip, (1, 2, 0))  # HWC for ultralytics
            for res in model(img, verbose=False):
                for box in res.boxes:
                    x0, y0, x1, y1 = (float(v) for v in box.xyxy[0].tolist())
                    detections.append(
                        Detection(
                            col0=t.col_off + x0, row0=t.row_off + y0,
                            col1=t.col_off + x1, row1=t.row_off + y1,
                            score=float(box.conf[0]), cls_name=str(names[int(box.cls[0])]),
                        )
                    )
    return merge.detections_to_features(detections, _affine6(transform), min_confidence=min_confidence)


def _run_water(ortho_path: str, transform) -> List[dict]:
    try:
        import numpy as np
        import rasterio
    except Exception:
        return []
    try:
        with rasterio.open(ortho_path) as src:
            rgb = np.transpose(src.read(indexes=[1, 2, 3], out_dtype="uint8"), (1, 2, 0))
        return spectral.detect_water_from_array(rgb, _affine6(transform))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Water detection failed: %s", exc)
        return []


def _run_slope(dtm_path: Optional[str], transform_ref: str) -> List[dict]:
    if not dtm_path or not Path(dtm_path).exists():
        return []
    try:
        import numpy as np
        import rasterio
    except Exception:
        return []
    try:
        with rasterio.open(dtm_path) as src:
            dtm = src.read(1, out_dtype="float32")
            # Approx pixel size in feet from the transform (degrees → feet at the
            # raster's latitude). Good enough for arrow spacing.
            from app.services.mission.geo import feet_per_degree_lat
            pixel_size_ft = abs(src.transform.e) * feet_per_degree_lat()
            return spectral.slope_arrows(dtm, _affine6(src.transform), pixel_size_ft)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Slope analysis failed: %s", exc)
        return []


def detect_features(
    ortho_tif: str,
    dtm_tif: Optional[str] = None,
    *,
    model_path: Optional[str] = None,
    min_confidence: Optional[float] = None,
) -> dict:
    """Run the full detection pipeline → GeoJSON FeatureCollection (spec §11.2)."""
    if not Path(ortho_tif).exists():
        raise FileNotFoundError(ortho_tif)

    # Settings are optional here so the pipeline can be driven directly in tests.
    if model_path is None or min_confidence is None:
        try:
            from app.config import get_settings

            s = get_settings()
            model_path = model_path or s.yolo_model_path
            min_confidence = s.feature_min_confidence if min_confidence is None else min_confidence
        except Exception:
            model_path = model_path or "models/yolov8n-aerial-property.pt"
            min_confidence = 0.45 if min_confidence is None else min_confidence

    try:
        import rasterio

        with rasterio.open(ortho_tif) as src:
            transform = src.transform
    except Exception as exc:  # noqa: BLE001
        logger.info("rasterio unavailable (%s) — returning empty FeatureCollection.", exc)
        return empty_feature_collection()

    features: List[dict] = []
    features += _run_yolo(ortho_tif, model_path, transform, min_confidence)
    features += _run_water(ortho_tif, transform)
    features += _run_slope(dtm_tif, ortho_tif)
    logger.info("Detected %d features in %s", len(features), ortho_tif)
    return merge.feature_collection(features)
