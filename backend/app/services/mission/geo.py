"""Lightweight geodesy helpers (standard library only).

The grid planner works in a local east/north tangent plane measured in **feet**
(US contractor standard, spec §14.2). For the parcel-scale areas this system
deals with (a few hundred feet across) a simple equirectangular projection about
the polygon centroid is more than accurate enough — sub-foot error over the
working area, well within the ±1 ft accuracy noted in spec §9.2.
"""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

# Mean Earth radius in feet (WGS84 authalic radius 6371008.8 m × 3.280839895).
EARTH_RADIUS_FT = 20902231.0
FEET_PER_METER = 3.280839895
METERS_PER_FOOT = 0.3048

Coord = Tuple[float, float]  # (lng, lat) — GeoJSON axis order


def feet_per_degree_lat() -> float:
    """Feet per degree of latitude (very nearly constant)."""
    return EARTH_RADIUS_FT * math.pi / 180.0


def feet_per_degree_lng(lat_deg: float) -> float:
    """Feet per degree of longitude at the given latitude."""
    return EARTH_RADIUS_FT * math.pi / 180.0 * math.cos(math.radians(lat_deg))


def ring_centroid(ring: Sequence[Coord]) -> Coord:
    """Area-weighted centroid of a closed polygon ring (lng, lat)."""
    pts = list(ring)
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(a) < 1e-12:  # degenerate — fall back to vertex mean
        n = len(pts) - 1
        return (sum(p[0] for p in pts[:-1]) / n, sum(p[1] for p in pts[:-1]) / n)
    a *= 0.5
    return (cx / (6 * a), cy / (6 * a))


class LocalPlane:
    """Convert between (lng, lat) degrees and local (east, north) feet."""

    def __init__(self, origin: Coord):
        self.origin_lng, self.origin_lat = origin
        self._fpd_lat = feet_per_degree_lat()
        self._fpd_lng = feet_per_degree_lng(self.origin_lat)

    def to_feet(self, coord: Coord) -> Tuple[float, float]:
        lng, lat = coord
        east = (lng - self.origin_lng) * self._fpd_lng
        north = (lat - self.origin_lat) * self._fpd_lat
        return east, north

    def to_lnglat(self, east: float, north: float) -> Coord:
        lng = self.origin_lng + east / self._fpd_lng
        lat = self.origin_lat + north / self._fpd_lat
        return (lng, lat)


def bounding_box_ft(plane: LocalPlane, ring: Sequence[Coord]) -> Tuple[float, float, float, float]:
    """Axis-aligned bounding box of a ring in local feet: (min_e, min_n, max_e, max_n)."""
    pts = [plane.to_feet(c) for c in ring]
    es = [p[0] for p in pts]
    ns = [p[1] for p in pts]
    return min(es), min(ns), max(es), max(ns)


def point_in_ring(east: float, north: float, ring_ft: Sequence[Tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon test in the local feet plane."""
    inside = False
    n = len(ring_ft)
    j = n - 1
    for i in range(n):
        xi, yi = ring_ft[i]
        xj, yj = ring_ft[j]
        if ((yi > north) != (yj > north)) and (
            east < (xj - xi) * (north - yi) / (yj - yi + 1e-15) + xi
        ):
            inside = not inside
        j = i
    return inside


def polygon_dimensions_ft(plane: LocalPlane, ring: Sequence[Coord]) -> Tuple[float, float]:
    """Width (E–W) and height (N–S) of a ring's bounding box, in feet."""
    min_e, min_n, max_e, max_n = bounding_box_ft(plane, ring)
    return (max_e - min_e, max_n - min_n)
