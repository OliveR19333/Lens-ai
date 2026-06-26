"""Map 2 — Elevation change map renderer (spec §9.2).

Grayscale hillshade from the DSM + 1 ft minor / 5 ft major contours from the DTM,
shared parcel boundary / grid / feature markers, scale bar, north arrow, title
block. Grayscale only (printer-safe). All elevation in **feet** (spec §14.2).

The hillshade + contours require rasterio (GDAL) and the DSM/DTM GeoTIFFs. When
those aren't available the sheet still renders with the boundary, grid, and a
note — so the framing/scale match Map 1 exactly.
"""
from __future__ import annotations

import logging
from pathlib import Path

from app.services.maps.layout import build_layout
from app.services.maps.scale import PrintScale, compute_print_scale
from app.services.maps import render_common as rc

logger = logging.getLogger("gas.maps.elev")


def _raster_to_page_grid(src, layout):
    """Build page-inch meshgrid (X, Y) for a raster's pixel centers."""
    import numpy as np
    from rasterio.warp import transform as warp_transform

    rows, cols = src.height, src.width
    # Pixel-center coordinates in the raster CRS → lon/lat → feet → page inches.
    xs = np.arange(cols) + 0.5
    ys = np.arange(rows) + 0.5
    xv, yv = np.meshgrid(xs, ys)
    east, north = src.transform * (xv.ravel(), yv.ravel())
    lon, lat = warp_transform(src.crs, "EPSG:4326", east.tolist(), north.tolist())
    plane = layout.plane
    px = np.empty(len(lon))
    py = np.empty(len(lat))
    for i, (lo, la) in enumerate(zip(lon, lat)):
        e, n = plane.to_feet((lo, la))
        px[i], py[i] = layout.world_to_page_in(e, n)
    return px.reshape(rows, cols), py.reshape(rows, cols)


def _try_draw_elevation(ax, layout, dsm_tif, dtm_tif, minor_ft, major_ft) -> bool:
    if not dtm_tif or not Path(dtm_tif).exists():
        return False
    try:
        import numpy as np
        import rasterio
    except Exception:
        logger.info("rasterio unavailable — elevation map rendered without terrain.")
        return False
    try:
        # Hillshade from DSM (optional).
        if dsm_tif and Path(dsm_tif).exists():
            with rasterio.open(dsm_tif) as dsrc:
                dsm = dsrc.read(1, out_dtype="float32")
                X, Y = _raster_to_page_grid(dsrc, layout)
            hs = _hillshade(dsm)
            ax.pcolormesh(X, Y, hs, cmap="gray", shading="auto", zorder=0, alpha=0.9)

        with rasterio.open(dtm_tif) as tsrc:
            dtm = tsrc.read(1, out_dtype="float32")
            Xc, Yc = _raster_to_page_grid(tsrc, layout)
        dtm = np.where(np.isfinite(dtm), dtm, np.nan)
        lo, hi = np.nanmin(dtm), np.nanmax(dtm)
        minor_levels = _levels(lo, hi, minor_ft)
        major_levels = _levels(lo, hi, major_ft)
        if len(minor_levels):
            ax.contour(Xc, Yc, dtm, levels=minor_levels, colors="0.45", linewidths=0.3, zorder=2)
        if len(major_levels):
            cs = ax.contour(Xc, Yc, dtm, levels=major_levels, colors="black", linewidths=0.8, zorder=3)
            ax.clabel(cs, fontsize=5, fmt="%d")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to draw elevation layers: %s", exc)
        return False


def _hillshade(arr, azimuth=315.0, altitude=45.0):
    import numpy as np

    x, y = np.gradient(arr)
    slope = np.pi / 2.0 - np.arctan(np.hypot(x, y))
    aspect = np.arctan2(-x, y)
    az = np.radians(360.0 - azimuth + 90.0)
    alt = np.radians(altitude)
    shaded = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
    return (shaded + 1) / 2.0


def _levels(lo, hi, step):
    import math

    import numpy as np

    if not (hi > lo) or step <= 0:
        return np.array([])
    start = math.ceil(lo / step) * step
    return np.arange(start, hi, step)


def render_elevation_map(
    parcel_geojson: dict,
    out_pdf: str | Path,
    *,
    dsm_tif: str | None = None,
    dtm_tif: str | None = None,
    features_geojson: dict | None = None,
    address: str = "",
    county: str = "",
    minor_contour_ft: int = 1,
    major_contour_ft: int = 5,
    grid_interval_ft: int = 10,
    dpi: int = 300,
) -> PrintScale:
    """Render Map 2 to ``out_pdf``; return the locked print scale."""
    scale = compute_print_scale(parcel_geojson)
    layout = build_layout(parcel_geojson, scale.feet_per_inch)

    fig, ax = rc.new_page()
    has_elev = _try_draw_elevation(ax, layout, dsm_tif, dtm_tif, minor_contour_ft, major_contour_ft)
    rc.draw_grid(ax, layout, grid_interval_ft)
    rc.draw_boundary(ax, layout)
    rc.draw_features(ax, layout, features_geojson)
    rc.draw_scale_bar(ax, layout, scale.note)
    rc.draw_north_arrow(ax)
    rc.draw_title_block(
        ax, title="Elevation Change Map", address=address, county=county,
        scale_label=scale.label,
    )
    note = (
        f"Contours: {minor_contour_ft} ft minor / {major_contour_ft} ft major · ±1 ft accuracy (GCP-free GPS)"
        if has_elev
        else "Elevation layers need DSM/DTM from WebODM — grid sheet shown at scale"
    )
    ax.text(4.25, 0.3, note, fontsize=6, ha="center", color="0.4")

    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, dpi=dpi, format="pdf")
    import matplotlib.pyplot as plt

    plt.close(fig)
    logger.info("Wrote elevation map %s (%s, terrain=%s)", out_pdf, scale.label, has_elev)
    return scale
