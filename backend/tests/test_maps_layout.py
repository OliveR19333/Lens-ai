"""Tests for the print-page layout math (spec §9)."""
from app.services.maps.layout import build_layout, _nice_number
from app.services.maps.scale import compute_print_scale


def test_layout_fits_printable_area(square_parcel):
    scale = compute_print_scale(square_parcel)  # 40 ft/in
    layout = build_layout(square_parcel, scale.feet_per_inch)
    # 300×400 ft at 40 ft/in → 7.5 × 10 inches.
    assert abs(layout.draw_w_in - 7.5) < 0.05
    assert abs(layout.draw_h_in - 10.0) < 0.05
    # Centered on the 8.5×11 sheet → ~0.5" margins.
    assert abs(layout.origin_x_in - 0.5) < 0.05
    assert abs(layout.origin_y_in - 0.5) < 0.05


def test_world_to_page_transform_endpoints(square_parcel):
    scale = compute_print_scale(square_parcel)
    layout = build_layout(square_parcel, scale.feet_per_inch)
    x0, y0 = layout.world_to_page_in(layout.min_e, layout.min_n)
    x1, y1 = layout.world_to_page_in(layout.min_e + layout.width_ft, layout.min_n + layout.height_ft)
    assert abs(x0 - layout.origin_x_in) < 1e-6
    assert abs(x1 - (layout.origin_x_in + layout.draw_w_in)) < 1e-6
    assert y1 > y0


def test_grid_lines_spacing(square_parcel):
    scale = compute_print_scale(square_parcel)
    layout = build_layout(square_parcel, scale.feet_per_inch)
    es, ns = layout.grid_lines_ft(10)
    # ~300 ft wide / 10 ft → ~30 lines; ~400/10 → ~40 lines.
    assert 28 <= len(es) <= 32
    assert 38 <= len(ns) <= 42


def test_scale_bar_is_a_nice_number(square_parcel):
    scale = compute_print_scale(square_parcel)
    layout = build_layout(square_parcel, scale.feet_per_inch)
    bar_ft, bar_in = layout.scale_bar(target_in=2.0)
    assert bar_ft in (50, 100, 25, 20, 200, 250)  # a "nice" round length
    assert abs(bar_in - bar_ft / scale.feet_per_inch) < 1e-9


def test_nice_number():
    assert _nice_number(73) == 100
    assert _nice_number(8) == 10
    assert _nice_number(2.1) == 2.5
    assert _nice_number(40) == 50
