"""Best-fit print-scale calculation (spec §9.3).

Auto-calculates the scale denominator (feet per inch) needed to fit a parcel on
an 8.5" × 11" sheet with 0.5" margins (printable area 7.5" × 10"), rounded up to
the nearest 5 ft so the scale bar lands on clean intervals. Also reports the
proportional enlargement factor for 25" × 30" grid paper.

Pure standard library — mirrors the spec pseudocode exactly so output is
verifiable in tests.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from app.services.mission.geo import (
    LocalPlane,
    polygon_dimensions_ft,
    ring_centroid,
)

PRINTABLE_WIDTH_IN = 7.5
PRINTABLE_HEIGHT_IN = 10.0
TARGET_GRID_WIDTH_IN = 25.0
TARGET_GRID_HEIGHT_IN = 30.0
PAPER_WIDTH_IN = 8.5
PAPER_HEIGHT_IN = 11.0


@dataclass
class PrintScale:
    feet_per_inch: int               # e.g. 40  → 1" = 40 ft
    parcel_width_ft: float
    parcel_height_ft: float
    enlargement_factor: float        # to reach 25" × 30" grid paper
    label: str                       # "1 inch = 40 feet"
    note: str                        # full on-map note incl. enlargement

    def as_dict(self) -> dict:
        return {
            "feet_per_inch": self.feet_per_inch,
            "parcel_width_ft": round(self.parcel_width_ft, 1),
            "parcel_height_ft": round(self.parcel_height_ft, 1),
            "enlargement_factor": round(self.enlargement_factor, 2),
            "label": self.label,
            "note": self.note,
        }


def _outer_ring(parcel_geojson: dict):
    geom = parcel_geojson
    if geom.get("type") == "Feature":
        geom = geom["geometry"]
    if geom.get("type") == "FeatureCollection":
        geom = geom["features"][0]["geometry"]
    if geom["type"] == "Polygon":
        return [(float(x), float(y)) for x, y in geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [(float(x), float(y)) for x, y in geom["coordinates"][0][0]]
    raise ValueError(f"Unsupported geometry type: {geom['type']}")


def compute_print_scale(parcel_geojson: dict, round_to_ft: int = 5) -> PrintScale:
    """Compute the locked best-fit print scale for a parcel polygon."""
    ring = _outer_ring(parcel_geojson)
    plane = LocalPlane(ring_centroid(ring))
    width_ft, height_ft = polygon_dimensions_ft(plane, ring)

    scale_w = width_ft / PRINTABLE_WIDTH_IN
    scale_h = height_ft / PRINTABLE_HEIGHT_IN
    raw = max(scale_w, scale_h)
    feet_per_inch = int(math.ceil(raw / round_to_ft) * round_to_ft) if raw > 0 else round_to_ft

    # Proportional enlargement to the larger grid paper (use width ratio; spec
    # notes 25/8.5 ≈ 2.94×, height 30/11 ≈ 2.73× — width is the binding ratio).
    enlargement = TARGET_GRID_WIDTH_IN / PAPER_WIDTH_IN

    label = f"1 inch = {feet_per_inch} feet"
    note = (
        f"Scale: {label} | Enlarge {enlargement:.2f}x for "
        f"{int(TARGET_GRID_WIDTH_IN)}x{int(TARGET_GRID_HEIGHT_IN)} grid"
    )
    return PrintScale(
        feet_per_inch=feet_per_inch,
        parcel_width_ft=width_ft,
        parcel_height_ft=height_ft,
        enlargement_factor=enlargement,
        label=label,
        note=note,
    )
