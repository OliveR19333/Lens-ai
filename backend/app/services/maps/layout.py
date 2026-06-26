"""Print-page layout math for the planning maps (spec §9).

Pure standard library — no matplotlib. Turns a parcel polygon + a locked
feet-per-inch scale into everything a renderer needs to place ink on an
8.5"×11" sheet: the world→page-inches transform, real-world grid line
positions, and a "nice" scale-bar length. Unit-tested so the cartography is
verifiable without a rendering backend.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Tuple

from app.services.mission.geo import LocalPlane, bounding_box_ft, ring_centroid
from app.services.maps.scale import (
    PAPER_WIDTH_IN,
    PAPER_HEIGHT_IN,
    PRINTABLE_WIDTH_IN,
    PRINTABLE_HEIGHT_IN,
)


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


def _nice_number(x: float) -> float:
    """Round x up to the nearest 1/2/2.5/5 × 10^k (for scale-bar lengths)."""
    if x <= 0:
        return 1.0
    exp = math.floor(math.log10(x))
    base = 10 ** exp
    for m in (1, 2, 2.5, 5, 10):
        if x <= m * base:
            return m * base
    return 10 * base


@dataclass
class PageLayout:
    feet_per_inch: int
    # Parcel ring projected to local feet (east, north).
    ring_ft: List[Tuple[float, float]]
    min_e: float
    min_n: float
    width_ft: float
    height_ft: float
    # Drawing size + bottom-left origin on the page, in inches.
    draw_w_in: float
    draw_h_in: float
    origin_x_in: float
    origin_y_in: float
    paper_w_in: float = PAPER_WIDTH_IN
    paper_h_in: float = PAPER_HEIGHT_IN
    plane: LocalPlane = field(default=None, repr=False)

    def world_to_page_in(self, east: float, north: float) -> Tuple[float, float]:
        """Local feet → page inches (origin at sheet bottom-left)."""
        return (
            self.origin_x_in + (east - self.min_e) / self.feet_per_inch,
            self.origin_y_in + (north - self.min_n) / self.feet_per_inch,
        )

    def ring_page_in(self) -> List[Tuple[float, float]]:
        return [self.world_to_page_in(e, n) for e, n in self.ring_ft]

    def grid_lines_ft(self, interval_ft: int) -> Tuple[List[float], List[float]]:
        """World-coordinate positions (east list, north list) of grid lines."""
        max_e = self.min_e + self.width_ft
        max_n = self.min_n + self.height_ft
        start_e = math.ceil(self.min_e / interval_ft) * interval_ft
        start_n = math.ceil(self.min_n / interval_ft) * interval_ft
        es = []
        e = start_e
        while e <= max_e:
            es.append(e)
            e += interval_ft
        ns = []
        n = start_n
        while n <= max_n:
            ns.append(n)
            n += interval_ft
        return es, ns

    def scale_bar(self, target_in: float = 2.0) -> Tuple[float, float]:
        """A nice round scale-bar length: returns (feet, inches)."""
        target_ft = target_in * self.feet_per_inch
        bar_ft = _nice_number(target_ft)
        return bar_ft, bar_ft / self.feet_per_inch


def build_layout(parcel_geojson: dict, feet_per_inch: int) -> PageLayout:
    """Compute the page layout for a parcel at a locked feet-per-inch scale."""
    ring = _outer_ring(parcel_geojson)
    plane = LocalPlane(ring_centroid(ring))
    ring_ft = [plane.to_feet(c) for c in ring]
    min_e, min_n, max_e, max_n = bounding_box_ft(plane, ring)
    width_ft = max_e - min_e
    height_ft = max_n - min_n

    draw_w_in = width_ft / feet_per_inch
    draw_h_in = height_ft / feet_per_inch
    # Center the parcel on the sheet (scale was chosen so it fits the printable
    # 7.5×10 area, so centering keeps ≥0.5" margins).
    origin_x_in = (PAPER_WIDTH_IN - draw_w_in) / 2.0
    origin_y_in = (PAPER_HEIGHT_IN - draw_h_in) / 2.0

    return PageLayout(
        feet_per_inch=feet_per_inch,
        ring_ft=ring_ft,
        min_e=min_e,
        min_n=min_n,
        width_ft=width_ft,
        height_ft=height_ft,
        draw_w_in=draw_w_in,
        draw_h_in=draw_h_in,
        origin_x_in=origin_x_in,
        origin_y_in=origin_y_in,
        plane=plane,
    )
