"""Map 2 — Elevation change map renderer (spec §9.2).

⚙ STUB — Phase 3. Grayscale hillshade from the DSM, 1 ft minor / 5 ft major
contours, flow-direction slope arrows at 50 ft spacing from the DTM aspect,
shared feature markers, spot elevations, grayscale only (printer-safe). All
elevation in feet (spec §14.2). Same locked print scale as Map 1.
"""
from __future__ import annotations

import logging
from pathlib import Path

from .scale import PrintScale, compute_print_scale

logger = logging.getLogger("gas.maps.elev")


def render_elevation_map(
    dsm_tif: str,
    dtm_tif: str,
    parcel_geojson: dict,
    features_geojson: dict | None,
    out_pdf: str | Path,
    *,
    address: str = "",
    county: str = "",
    minor_contour_ft: int = 1,
    major_contour_ft: int = 5,
    slope_arrow_spacing_ft: int = 50,
    dpi: int = 300,
) -> PrintScale:
    """Render Map 2 to ``out_pdf``; return the locked print scale.

    ⚙ TODO (spec §9.2 / §9.4):
        1. hillshade(DSM) → grayscale terrain-relief base
        2. contours from DTM: minor every `minor_contour_ft`, major bold every `major_contour_ft`
        3. slope arrows from DTM aspect at `slope_arrow_spacing_ft`
        4. feature markers (same as Map 1) + spot elevations at corners/high/low
        5. grayscale only; scale bar + ratio + north arrow + title block
        6. savefig(out_pdf, dpi=dpi)
    """
    scale = compute_print_scale(parcel_geojson)
    logger.info(
        "render_elevation_map STUB → %s  (%s, contours %d/%dft)",
        out_pdf,
        scale.label,
        minor_contour_ft,
        major_contour_ft,
    )
    raise NotImplementedError(
        "Elevation map rendering not implemented (spec §9.2). Accuracy note: "
        "±1 ft, GCP-free drone GPS positioning."
    )
