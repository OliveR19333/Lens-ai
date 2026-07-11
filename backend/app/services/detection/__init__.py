"""AI feature detection over the orthomosaic (spec §8).

Pure, testable core (tiling, geo-transform, detection merge/NMS, confidence
filtering, GeoJSON assembly) plus lazily-imported heavy stages (YOLOv8 via
ultralytics, spectral water via numpy/rasterio, slope via the DTM).
"""
from .pipeline import detect_features  # noqa: F401
