"""Spectral water detection + DTM slope analysis (spec §8.3).

The array-level math is plain numpy (unit-tested with synthetic arrays). Thin
wrappers read the GeoTIFFs via rasterio (lazy import) and hand the arrays to the
pure functions, so the detection logic is verifiable without GDAL.
"""
from __future__ import annotations

import math
from collections import deque
from typing import List, Tuple

from app.services.detection.geotransform import Affine6, bbox_to_ring, ring_area_sqft

# HSV blue range for water/ponds (spec §8.3 — "HSV blue range"). Hue in [0,1].
WATER_HUE_MIN = 0.50   # ~180°
WATER_HUE_MAX = 0.72   # ~260°
WATER_SAT_MIN = 0.18
WATER_VAL_MIN = 0.12


def water_mask(rgb):
    """Boolean mask of water-like (blue) pixels from an HxWx3 uint8/float RGB array."""
    import numpy as np
    from matplotlib.colors import rgb_to_hsv

    arr = np.asarray(rgb, dtype="float32")
    if arr.max() > 1.0:
        arr = arr / 255.0
    hsv = rgb_to_hsv(arr[..., :3])
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return (
        (h >= WATER_HUE_MIN) & (h <= WATER_HUE_MAX) & (s >= WATER_SAT_MIN) & (v >= WATER_VAL_MIN)
    )


def mask_to_boxes(mask, min_pixels: int = 200) -> List[Tuple[int, int, int, int]]:
    """Connected-components (4-conn) → pixel bboxes (col0,row0,col1,row1).

    Plain BFS so it needs no scipy. Suited to the modest masks parcels produce.
    """
    import numpy as np

    m = np.asarray(mask, dtype=bool)
    rows, cols = m.shape
    visited = np.zeros_like(m, dtype=bool)
    boxes: List[Tuple[int, int, int, int]] = []
    for r0 in range(rows):
        for c0 in range(cols):
            if not m[r0, c0] or visited[r0, c0]:
                continue
            q = deque([(r0, c0)])
            visited[r0, c0] = True
            minr = maxr = r0
            minc = maxc = c0
            count = 0
            while q:
                r, c = q.popleft()
                count += 1
                minr, maxr = min(minr, r), max(maxr, r)
                minc, maxc = min(minc, c), max(maxc, c)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and m[nr, nc] and not visited[nr, nc]:
                        visited[nr, nc] = True
                        q.append((nr, nc))
            if count >= min_pixels:
                boxes.append((minc, minr, maxc + 1, maxr + 1))
    return boxes


def detect_water_from_array(rgb, transform: Affine6, *, min_pixels: int = 200) -> List[dict]:
    """Spectral water features (spec §11.2) from an RGB array + geo-transform."""
    boxes = mask_to_boxes(water_mask(rgb), min_pixels=min_pixels)
    features = []
    for c0, r0, c1, r1 in boxes:
        ring = bbox_to_ring(transform, c0, r0, c1, r1)
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[list(p) for p in ring]]},
                "properties": {
                    "feature_type": "pond",
                    "label": "Pond",
                    "confidence": 0.6,  # heuristic (non-ML) detector
                    "area_sqft": round(ring_area_sqft(ring), 1),
                    "notes": "spectral",
                },
            }
        )
    return features


def slope_aspect(dtm, pixel_size_ft: float):
    """(slope_degrees, aspect_degrees) arrays from a DTM elevation array (feet)."""
    import numpy as np

    arr = np.asarray(dtm, dtype="float32")
    # np.gradient → (d/drow, d/dcol); +col = east, +row = south.
    dzdy, dzdx = np.gradient(arr, pixel_size_ft)
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    # Downhill flow direction as a math angle (0°=east, 90°=north): downhill =
    # -gradient, with the north component flipped because row increases south.
    aspect = np.degrees(np.arctan2(dzdy, -dzdx))
    aspect = (aspect + 360.0) % 360.0
    return slope, aspect


def slope_arrows(dtm, transform: Affine6, pixel_size_ft: float, *, spacing_px: int = 50,
                 min_slope_deg: float = 2.0) -> List[dict]:
    """Flow-direction arrow features at a grid spacing (spec §8.3 / §9.2).

    Each arrow is a 2-point LineString pointing downhill, emitted only where the
    local slope exceeds ``min_slope_deg``.
    """
    import numpy as np

    slope, aspect = slope_aspect(dtm, pixel_size_ft)
    rows, cols = slope.shape
    feats = []
    for r in range(spacing_px // 2, rows, spacing_px):
        for c in range(spacing_px // 2, cols, spacing_px):
            s = float(slope[r, c])
            if s < min_slope_deg:
                continue
            # Downhill direction = aspect; build a short arrow in pixel space.
            ang = math.radians(float(aspect[r, c]))
            dx, dy = math.cos(ang) * spacing_px * 0.4, -math.sin(ang) * spacing_px * 0.4
            p0 = bbox_to_ring(transform, c, r, c, r)[0]
            p1 = bbox_to_ring(transform, c + dx, r + dy, c + dx, r + dy)[0]
            feats.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [list(p0), list(p1)]},
                    "properties": {
                        "feature_type": "slope",
                        "label": "Slope",
                        "confidence": 1.0,
                        "slope_deg": round(s, 1),
                        "notes": "flow direction",
                    },
                }
            )
    return feats
