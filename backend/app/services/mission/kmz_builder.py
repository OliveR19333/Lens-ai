"""Assemble a DJI-compatible mapping ``.kmz`` (spec §6.2 / §6.3).

A DJI mapping KMZ is a zip archive with the layout::

    mission.kmz
    └── wpmz/
        ├── template.kml      ← area boundary polygon
        └── waylines.wpml     ← flight path, altitude, overlap settings

This module is the public entry point of the ``mission`` package and depends
only on the standard library, so it can run in CI and (transpiled) client-side.
"""
from __future__ import annotations

import io
import zipfile
from dataclasses import asdict, dataclass
from typing import Optional

from .geo import Coord
from .grid import Camera, GridPlan, _outer_ring, plan_grid
from .wpml import DRONE_ENUM, build_template_kml, build_waylines_wpml


@dataclass
class MissionParams:
    """Inputs for one mission generation (spec §6.1 flight parameters)."""

    altitude_ft: float = 120.0       # adjustable 80–200
    forward_overlap: float = 0.80
    side_overlap: float = 0.75
    buffer_ft: float = 15.0
    auto_flight_speed_mps: float = 6.0
    finish_action: str = "goHome"
    drone: str = "mini4pro"

    def validate(self) -> None:
        if not (80.0 <= self.altitude_ft <= 200.0):
            raise ValueError("altitude_ft must be between 80 and 200 ft (spec §6.1).")
        if self.drone not in DRONE_ENUM:
            raise ValueError(f"Unknown drone '{self.drone}'. Known: {list(DRONE_ENUM)}")


@dataclass
class MissionResult:
    kmz_bytes: bytes
    plan: GridPlan
    template_kml: str
    waylines_wpml: str

    def summary(self) -> dict:
        return {
            "waypoints": len(self.plan.waypoints),
            "line_count": self.plan.line_count,
            "line_spacing_ft": self.plan.line_spacing_ft,
            "photo_spacing_ft": self.plan.photo_spacing_ft,
            "flight_axis": self.plan.flight_axis,
            "altitude_ft": self.plan.altitude_ft,
            "estimated_photos": self.plan.estimated_photos,
            "kmz_size_bytes": len(self.kmz_bytes),
        }


def build_mission_kmz(
    parcel_geojson: dict,
    params: Optional[MissionParams] = None,
    camera: Optional[Camera] = None,
) -> MissionResult:
    """Generate a DJI mapping KMZ from a parcel boundary GeoJSON polygon.

    Implements spec §6.3:
      1. receive parcel boundary GeoJSON polygon
      2/3. bbox + 15 ft buffer, compute grid lines at altitude/overlap
      4. waypoints with photo trigger intervals
      5. build ``waylines.wpml`` + ``template.kml``
      6. zip into ``.kmz``
    """
    params = params or MissionParams()
    params.validate()

    drone_enum = DRONE_ENUM[params.drone]
    ring = _outer_ring(parcel_geojson)

    plan = plan_grid(
        parcel_geojson,
        altitude_ft=params.altitude_ft,
        forward_overlap=params.forward_overlap,
        side_overlap=params.side_overlap,
        buffer_ft=params.buffer_ft,
        camera=camera,
    )

    template_kml = build_template_kml(
        ring, drone_enum=drone_enum, finish_action=params.finish_action
    )
    waylines_wpml = build_waylines_wpml(
        plan,
        drone_enum=drone_enum,
        finish_action=params.finish_action,
        auto_flight_speed_mps=params.auto_flight_speed_mps,
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("wpmz/template.kml", template_kml)
        zf.writestr("wpmz/waylines.wpml", waylines_wpml)
    return MissionResult(
        kmz_bytes=buf.getvalue(),
        plan=plan,
        template_kml=template_kml,
        waylines_wpml=waylines_wpml,
    )
