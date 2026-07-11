"""Shared cartographic drawing helpers for the planning maps (spec §9.1/§9.2).

Everything is drawn in **page inches** on an 8.5"×11" sheet so the two maps share
identical framing and the locked scale. Matplotlib is imported lazily by the
renderers; these helpers receive an Axes already set up in inch coordinates.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import List, Optional, Tuple

from app.services.maps.layout import PageLayout
from app.services.mission.geo import LocalPlane

# Feature marker glyphs (printer-safe, grayscale) keyed by spec §8.2 classes.
FEATURE_STYLE = {
    "pond": ("o", "Pond"),
    "water": ("o", "Water"),
    "trees": ("^", "Trees"),
    "structure": ("s", "Structure"),
    "building": ("s", "Structure"),
    "driveway": ("D", "Driveway"),
    "fence": ("|", "Fence"),
    "slope": (">", "Slope"),
}


def new_page():
    """Create an 8.5×11 figure + an Axes in inch coordinates."""
    import matplotlib

    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 11)
    ax.axis("off")
    return fig, ax


def draw_grid(ax, layout: PageLayout, interval_ft: int) -> None:
    """Measured grid at real-world intervals, clipped to the parcel bbox."""
    es, ns = layout.grid_lines_ft(interval_ft)
    y0 = layout.origin_y_in
    y1 = layout.origin_y_in + layout.draw_h_in
    x0 = layout.origin_x_in
    x1 = layout.origin_x_in + layout.draw_w_in
    for e in es:
        x, _ = layout.world_to_page_in(e, layout.min_n)
        ax.plot([x, x], [y0, y1], color="0.75", linewidth=0.4, zorder=1)
    for n in ns:
        _, y = layout.world_to_page_in(layout.min_e, n)
        ax.plot([x0, x1], [y, y], color="0.75", linewidth=0.4, zorder=1)


def draw_boundary(ax, layout: PageLayout) -> None:
    """Bold black parcel outline (3pt) + dashed 50% inset (spec §9.1)."""
    from matplotlib.patches import Polygon as MplPolygon

    pts = layout.ring_page_in()
    ax.add_patch(MplPolygon(pts, closed=True, fill=False, edgecolor="black", linewidth=3, zorder=5))
    ax.add_patch(
        MplPolygon(
            pts, closed=True, fill=False, edgecolor="black", linewidth=1,
            linestyle=(0, (4, 3)), alpha=0.5, zorder=5,
        )
    )


def _ring_centroid_lnglat(coords) -> Tuple[float, float]:
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def draw_features(ax, layout: PageLayout, features_geojson: Optional[dict]) -> None:
    """Labeled markers for detected features (spec §8.2 / §9.1)."""
    if not features_geojson:
        return
    plane: LocalPlane = layout.plane
    for feat in features_geojson.get("features", []):
        geom = feat.get("geometry") or {}
        props = feat.get("properties") or {}
        ftype = (props.get("feature_type") or "").lower()
        marker, default_label = FEATURE_STYLE.get(ftype, ("x", ftype.capitalize() or "Feature"))
        label = props.get("label") or default_label

        if geom.get("type") == "Point":
            lng, lat = geom["coordinates"][0], geom["coordinates"][1]
        elif geom.get("type") == "Polygon":
            lng, lat = _ring_centroid_lnglat(geom["coordinates"][0])
        elif geom.get("type") == "MultiPolygon":
            lng, lat = _ring_centroid_lnglat(geom["coordinates"][0][0])
        else:
            continue
        e, n = plane.to_feet((lng, lat))
        x, y = layout.world_to_page_in(e, n)
        ax.plot([x], [y], marker=marker, markersize=7, markerfacecolor="white",
                markeredgecolor="black", markeredgewidth=1.2, zorder=6)
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(6, 4),
                    fontsize=6.5, family="sans-serif", zorder=6)


def draw_scale_bar(ax, layout: PageLayout, scale_note: str) -> None:
    """Graphical scale bar + ratio/enlargement text (spec §9.1)."""
    bar_ft, bar_in = layout.scale_bar()
    x0, y0 = 0.6, 0.55
    # Two-segment black/white bar.
    half = bar_in / 2
    ax.add_patch(_rect(x0, y0, half, 0.08, "black"))
    ax.add_patch(_rect(x0 + half, y0, half, 0.08, "white", edge="black"))
    ax.plot([x0, x0 + bar_in], [y0, y0], color="black", linewidth=0.8)
    ax.text(x0, y0 + 0.12, "0", fontsize=6, ha="center")
    ax.text(x0 + bar_in, y0 + 0.12, f"{int(bar_ft)} ft", fontsize=6, ha="center")
    ax.text(x0, y0 - 0.16, scale_note, fontsize=6.5, family="sans-serif")


def _rect(x, y, w, h, face, edge="none"):
    from matplotlib.patches import Rectangle

    return Rectangle((x, y), w, h, facecolor=face, edgecolor=edge, linewidth=0.6, zorder=4)


def draw_north_arrow(ax, x: float = 7.7, y: float = 9.9) -> None:
    """Simple true-north arrow (spec §9.1)."""
    ax.annotate(
        "N", xy=(x, y + 0.35), xytext=(x, y - 0.1), ha="center", fontsize=9, weight="bold",
        arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.5),
    )


_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "gas_logo_print.png"


def _draw_logo(ax) -> bool:
    """Stamp the GAS shield (inverted grayscale) at the title-block left."""
    if not _LOGO_PATH.exists():
        return False
    try:
        import matplotlib.image as mpimg

        img = mpimg.imread(str(_LOGO_PATH))
        ax.imshow(img, extent=(0.58, 1.12, 10.30, 10.84), zorder=6, aspect="auto")
        return True
    except Exception:  # noqa: BLE001 — logo is decorative, never fail the map
        return False


def draw_title_block(ax, *, title: str, address: str, county: str, scale_label: str,
                     date_str: Optional[str] = None) -> None:
    """Title block: logo, address, date, scale, county (spec §9.1)."""
    date_str = date_str or dt.date.today().isoformat()
    ax.add_patch(_rect(0.5, 10.25, 7.5, 0.6, "white", edge="black"))
    text_x = 1.25 if _draw_logo(ax) else 0.65
    ax.text(text_x, 10.62, title, fontsize=11, weight="bold", family="sans-serif")
    ax.text(text_x, 10.40, address or "—", fontsize=7.5, family="sans-serif")
    ax.text(7.85, 10.62, f"TNC GAS · {county.title() if county else ''}", fontsize=7.5,
            ha="right", family="sans-serif")
    ax.text(7.85, 10.40, f"{scale_label}  |  {date_str}", fontsize=7.5, ha="right",
            family="sans-serif")
