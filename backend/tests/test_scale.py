"""Tests for print-scale calculation (spec §9.3)."""
from app.services.maps.scale import compute_print_scale


def test_scale_matches_spec_example(square_parcel):
    """Spec §9.3 worked example: 300×400 ft parcel → 1" = 40 ft."""
    scale = compute_print_scale(square_parcel)
    assert scale.feet_per_inch == 40
    assert scale.label == "1 inch = 40 feet"
    # parcel dimensions recover the constructed size to within a foot
    assert abs(scale.parcel_width_ft - 300.0) < 2.0
    assert abs(scale.parcel_height_ft - 400.0) < 2.0


def test_scale_rounds_up_to_nearest_five(square_parcel):
    scale = compute_print_scale(square_parcel)
    assert scale.feet_per_inch % 5 == 0


def test_enlargement_factor_for_grid_paper(square_parcel):
    scale = compute_print_scale(square_parcel)
    # 25" / 8.5" ≈ 2.94 (spec §9.3)
    assert abs(scale.enlargement_factor - (25.0 / 8.5)) < 0.01
    assert "Enlarge" in scale.note


def test_small_parcel_minimum_scale():
    """A tiny parcel still yields a sane, multiple-of-5 scale."""
    tiny = {
        "type": "Polygon",
        "coordinates": [[[-83.97, 35.75], [-83.9699, 35.75],
                         [-83.9699, 35.7501], [-83.97, 35.7501], [-83.97, 35.75]]],
    }
    scale = compute_print_scale(tiny)
    assert scale.feet_per_inch >= 5
    assert scale.feet_per_inch % 5 == 0
