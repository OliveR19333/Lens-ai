"""Lawnmower / boustrophedon grid flight-line computation (spec §6.3).

Pure standard library. Works in the local feet plane (see ``geo.py``), then
projects waypoints back to (lng, lat). Photo spacing and line spacing are
derived from the camera footprint at the chosen altitude and the requested
forward/side overlaps.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

from .geo import (
    Coord,
    LocalPlane,
    bounding_box_ft,
    ring_centroid,
)


@dataclass(frozen=True)
class Camera:
    """Camera geometry used to size the photo grid.

    Defaults approximate the DJI Mini 4 Pro wide camera (1/1.3" sensor, 24 mm
    equivalent). Confirm against the airframe before relying on overlap numbers
    for survey-grade work.
    """

    name: str = "DJI Mini 4 Pro"
    sensor_width_mm: float = 9.6
    sensor_height_mm: float = 7.2
    focal_length_mm: float = 6.72  # real focal length (~24 mm equiv)

    def footprint_ft(self, altitude_ft: float) -> Tuple[float, float]:
        """Ground footprint (across, along) in feet at a nadir altitude."""
        across = altitude_ft * self.sensor_width_mm / self.focal_length_mm
        along = altitude_ft * self.sensor_height_mm / self.focal_length_mm
        return across, along


@dataclass
class Waypoint:
    lng: float
    lat: float
    altitude_ft: float
    take_photo: bool = True


@dataclass
class GridPlan:
    waypoints: List[Waypoint] = field(default_factory=list)
    line_spacing_ft: float = 0.0
    photo_spacing_ft: float = 0.0
    line_count: int = 0
    altitude_ft: float = 0.0
    flight_axis: str = "north-south"  # lines run along this axis
    estimated_photos: int = 0


def _outer_ring(geojson_polygon: dict) -> List[Coord]:
    """Extract the outer ring of a GeoJSON Polygon or first Polygon of a MultiPolygon."""
    geom = geojson_polygon
    if geom.get("type") == "Feature":
        geom = geom["geometry"]
    if geom.get("type") == "FeatureCollection":
        geom = geom["features"][0]["geometry"]
    if geom["type"] == "Polygon":
        ring = geom["coordinates"][0]
    elif geom["type"] == "MultiPolygon":
        ring = geom["coordinates"][0][0]
    else:
        raise ValueError(f"Unsupported geometry type: {geom['type']}")
    return [(float(x), float(y)) for x, y in ring]


def plan_grid(
    parcel_geojson: dict,
    altitude_ft: float = 120.0,
    forward_overlap: float = 0.80,
    side_overlap: float = 0.75,
    buffer_ft: float = 15.0,
    camera: Camera | None = None,
) -> GridPlan:
    """Build a lawnmower waypoint grid over a parcel polygon.

    Parameters mirror spec §6.1 flight parameters. The parcel bounding box is
    expanded by ``buffer_ft`` on every edge (spec §6.3 step 2). Flight lines run
    parallel to the longer bbox axis to minimise turns.
    """
    if not (0.0 <= forward_overlap < 1.0) or not (0.0 <= side_overlap < 1.0):
        raise ValueError("Overlaps must be in [0, 1).")
    if altitude_ft <= 0:
        raise ValueError("Altitude must be positive.")

    camera = camera or Camera()
    ring = _outer_ring(parcel_geojson)
    origin = ring_centroid(ring)
    plane = LocalPlane(origin)

    min_e, min_n, max_e, max_n = bounding_box_ft(plane, ring)
    min_e -= buffer_ft
    min_n -= buffer_ft
    max_e += buffer_ft
    max_n += buffer_ft

    width = max_e - min_e   # E–W extent
    height = max_n - min_n  # N–S extent

    across_ft, along_ft = camera.footprint_ft(altitude_ft)
    line_spacing = max(across_ft * (1.0 - side_overlap), 1.0)
    photo_spacing = max(along_ft * (1.0 - forward_overlap), 1.0)

    # Fly lines along the longer axis (fewer, longer passes).
    lines_along_north = height >= width
    flight_axis = "north-south" if lines_along_north else "east-west"

    waypoints: List[Waypoint] = []
    if lines_along_north:
        n_lines = max(int(math.ceil(width / line_spacing)) + 1, 1)
        for i in range(n_lines):
            e = min_e + i * line_spacing
            e = min(e, max_e)
            n_photos = max(int(math.ceil(height / photo_spacing)) + 1, 2)
            coords_n = [min(min_n + j * photo_spacing, max_n) for j in range(n_photos)]
            if i % 2 == 1:  # boustrophedon: reverse alternate lines
                coords_n = list(reversed(coords_n))
            for north in coords_n:
                lng, lat = plane.to_lnglat(e, north)
                waypoints.append(Waypoint(lng, lat, altitude_ft))
    else:
        n_lines = max(int(math.ceil(height / line_spacing)) + 1, 1)
        for i in range(n_lines):
            north = min_n + i * line_spacing
            north = min(north, max_n)
            n_photos = max(int(math.ceil(width / photo_spacing)) + 1, 2)
            coords_e = [min(min_e + j * photo_spacing, max_e) for j in range(n_photos)]
            if i % 2 == 1:
                coords_e = list(reversed(coords_e))
            for east in coords_e:
                lng, lat = plane.to_lnglat(east, north)
                waypoints.append(Waypoint(lng, lat, altitude_ft))

    return GridPlan(
        waypoints=waypoints,
        line_spacing_ft=round(line_spacing, 2),
        photo_spacing_ft=round(photo_spacing, 2),
        line_count=n_lines,
        altitude_ft=altitude_ft,
        flight_axis=flight_axis,
        estimated_photos=len(waypoints),
    )
