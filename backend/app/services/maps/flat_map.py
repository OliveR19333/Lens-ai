"""Map 1 — Flat planning map renderer (spec §9.1).

Grayscale orthomosaic base (optional) + bold parcel boundary, measured grid,
labeled feature markers, scale bar + ratio, north arrow, and title block,
exported to a print-ready PDF at ≥300 DPI on 8.5×11.

The orthomosaic underlay requires rasterio (GDAL). When the GeoTIFF or rasterio
is unavailable, the map still renders fully as a **scaled grid planning sheet** —
which is exactly what the irrigation/hardscape use cases need for hand drawing.
"""
from __future__ import annotations

import logging
from pathlib import Path

from app.services.maps.layout import build_layout
from app.services.maps.scale import PrintScale, compute_print_scale
from app.services.maps import render_common as rc

logger = logging.getLogger("gas.maps.flat")


def _try_draw_ortho(ax, layout, ortho_tif: str | None) -> bool:
    """Draw a grayscale orthomosaic underlay if rasterio + the file are present."""
    if not ortho_tif or not Path(ortho_tif).exists():
        return False
    try:
        import numpy as np
        import rasterio
        from rasterio.warp import transform_bounds
    except Exception:
        logger.info("rasterio unavailable — rendering flat map without raster underlay.")
        return False
    try:
        with rasterio.open(ortho_tif) as src:
            arr = src.read(out_dtype="float32")
            gray = arr.mean(axis=0)
            gray = (gray - gray.min()) / (gray.ptp() + 1e-9)
            left, bottom, right, top = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
        plane = layout.plane
        e0, n0 = plane.to_feet((left, bottom))
        e1, n1 = plane.to_feet((right, top))
        x0, y0 = layout.world_to_page_in(e0, n0)
        x1, y1 = layout.world_to_page_in(e1, n1)
        ax.imshow(gray, cmap="gray", extent=(x0, x1, y0, y1), zorder=0, aspect="auto")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to draw ortho underlay: %s", exc)
        return False


def render_flat_map(
    parcel_geojson: dict,
    out_pdf: str | Path,
    *,
    ortho_tif: str | None = None,
    features_geojson: dict | None = None,
    address: str = "",
    county: str = "",
    grid_interval_ft: int = 10,
    dpi: int = 300,
) -> PrintScale:
    """Render Map 1 to ``out_pdf``; return the locked print scale."""
    scale = compute_print_scale(parcel_geojson)
    layout = build_layout(parcel_geojson, scale.feet_per_inch)

    fig, ax = rc.new_page()
    has_ortho = _try_draw_ortho(ax, layout, ortho_tif)
    rc.draw_grid(ax, layout, grid_interval_ft)
    rc.draw_boundary(ax, layout)
    rc.draw_features(ax, layout, features_geojson)
    rc.draw_scale_bar(ax, layout, scale.note)
    rc.draw_north_arrow(ax)
    rc.draw_title_block(
        ax, title="Flat Planning Map", address=address, county=county,
        scale_label=scale.label,
    )
    if not has_ortho:
        ax.text(4.25, 0.3, "Grid planning sheet (no orthomosaic) — hand-annotate at scale",
                fontsize=6, ha="center", color="0.4")

    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, dpi=dpi, format="pdf")
    import matplotlib.pyplot as plt

    plt.close(fig)
    logger.info("Wrote flat map %s (%s, ortho=%s)", out_pdf, scale.label, has_ortho)
    return scale
