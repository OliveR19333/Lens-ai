"""Pixel ↔ world coordinate transforms for georeferencing detections (spec §8.3).

Works with a rasterio-style affine transform expressed as the 6-tuple
``(a, b, c, d, e, f)`` where::

    world_x = a*col + b*row + c
    world_y = d*col + e*row + f

For a north-up orthomosaic in EPSG:4326, ``a`` is the +x pixel size (degrees),
``e`` is the (negative) +y pixel size, ``c``/``f`` the top-left origin. Pure
standard library so detection georeferencing is unit-testable without GDAL.
"""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from app.services.mission.geo import LocalPlane

Affine6 = Tuple[float, float, float, float, float, float]


def pixel_to_world(transform: Affine6, col: float, row: float) -> Tuple[float, float]:
    a, b, c, d, e, f = transform
    return (a * col + b * row + c, d * col + e * row + f)


def bbox_to_ring(transform: Affine6, col0: float, row0: float, col1: float, row1: float) -> List[Tuple[float, float]]:
    """Pixel bbox (col0,row0)-(col1,row1) → closed world ring [(x,y), ...]."""
    corners = [(col0, row0), (col1, row0), (col1, row1), (col0, row1), (col0, row0)]
    return [pixel_to_world(transform, c, r) for c, r in corners]


def ring_area_sqft(ring: Sequence[Tuple[float, float]]) -> float:
    """Area of a world (lng,lat) ring in square feet (shoelace in a local plane)."""
    pts = list(ring)
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    # Centroid for the local tangent plane.
    cx = sum(p[0] for p in pts[:-1]) / (len(pts) - 1)
    cy = sum(p[1] for p in pts[:-1]) / (len(pts) - 1)
    plane = LocalPlane((cx, cy))
    fpts = [plane.to_feet(p) for p in pts]
    area = 0.0
    for (x0, y0), (x1, y1) in zip(fpts[:-1], fpts[1:]):
        area += x0 * y1 - x1 * y0
    return abs(area) / 2.0
