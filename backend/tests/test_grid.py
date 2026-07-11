"""Tests for the lawnmower grid planner (spec §6.3)."""
import math

from app.services.mission.grid import Camera, plan_grid


def test_grid_produces_waypoints(square_parcel):
    plan = plan_grid(square_parcel, altitude_ft=120, forward_overlap=0.80, side_overlap=0.75)
    assert plan.estimated_photos == len(plan.waypoints)
    assert plan.estimated_photos > 0
    assert plan.line_count >= 1


def test_flight_lines_run_along_longer_axis(square_parcel):
    # 300 (E–W) × 400 (N–S): longer axis is N–S, so lines run north-south.
    plan = plan_grid(square_parcel)
    assert plan.flight_axis == "north-south"


def test_higher_overlap_yields_more_waypoints(square_parcel):
    sparse = plan_grid(square_parcel, forward_overlap=0.60, side_overlap=0.60)
    dense = plan_grid(square_parcel, forward_overlap=0.85, side_overlap=0.85)
    assert dense.estimated_photos > sparse.estimated_photos


def test_spacing_derives_from_camera_and_altitude(square_parcel):
    cam = Camera()
    plan = plan_grid(square_parcel, altitude_ft=120, side_overlap=0.75)
    across, _ = cam.footprint_ft(120)
    expected = across * (1 - 0.75)
    assert math.isclose(plan.line_spacing_ft, round(expected, 2), rel_tol=1e-6)


def test_invalid_overlap_raises(square_parcel):
    for bad in (1.0, -0.1, 1.5):
        try:
            plan_grid(square_parcel, forward_overlap=bad)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_accepts_feature_and_featurecollection(square_parcel):
    feature = {"type": "Feature", "geometry": square_parcel, "properties": {}}
    fc = {"type": "FeatureCollection", "features": [feature]}
    assert plan_grid(feature).estimated_photos > 0
    assert plan_grid(fc).estimated_photos > 0
