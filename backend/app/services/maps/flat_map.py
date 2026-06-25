"""Map 1 — Flat planning map renderer (spec §9.1).

⚙ STUB — Phase 2. Renders a grayscale orthomosaic with bold parcel boundary,
labeled feature markers, a measured grid, scale bar + ratio, north arrow, and a
title block, exported to print-ready PDF at ≥300 DPI on 8.5×11.

Implementation options (spec §9.4): PyQGIS print layout, or
matplotlib + rasterio + geopandas. The latter is the lighter default.
"""
from __future__ import annotations

import logging
from pathlib import Path

from .scale import PrintScale, compute_print_scale

logger = logging.getLogger("gas.maps.flat")


def render_flat_map(
    ortho_tif: str,
    parcel_geojson: dict,
    features_geojson: dict | None,
    out_pdf: str | Path,
    *,
    address: str = "",
    county: str = "",
    grid_interval_ft: int = 10,
    dpi: int = 300,
) -> PrintScale:
    """Render Map 1 to ``out_pdf``; return the locked print scale.

    ⚙ TODO (spec §9.1 / §9.4):
        1. desaturate ortho GeoTIFF → grayscale base layer
        2. draw parcel boundary (3pt bold black, dashed 50% inset)
        3. overlay feature markers (pond/trees/structure/driveway/fence)
        4. measured grid at `grid_interval_ft` real-world intervals
        5. scale bar + ratio text, north arrow, title block
        6. savefig(out_pdf, dpi=dpi) — Arial/Helvetica labels
    """
    scale = compute_print_scale(parcel_geojson)
    logger.info(
        "render_flat_map STUB → %s  (%s, grid=%dft, %d DPI)",
        out_pdf,
        scale.label,
        grid_interval_ft,
        dpi,
    )
    raise NotImplementedError(
        "Flat map rendering not implemented (spec §9.1). Scale computed: "
        f"{scale.note}"
    )
