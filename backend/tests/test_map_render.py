"""Smoke tests that actually render the map PDFs (spec §9.1/§9.2).

Skipped automatically when matplotlib isn't installed (e.g. minimal CI), so the
suite still runs everywhere; when present, they prove a real PDF is produced.
"""
import pytest

matplotlib = pytest.importorskip("matplotlib")

from app.services.maps.flat_map import render_flat_map  # noqa: E402
from app.services.maps.elevation_map import render_elevation_map  # noqa: E402


def _features_near(parcel):
    # Place a couple of features inside the parcel bbox.
    ring = parcel["coordinates"][0]
    lng = (ring[0][0] + ring[2][0]) / 2
    lat = (ring[0][1] + ring[2][1]) / 2
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lng, lat]},
             "properties": {"feature_type": "pond", "label": "Pond"}},
        ],
    }


def _is_pdf(path):
    with open(path, "rb") as f:
        return f.read(5) == b"%PDF-"


def test_flat_map_writes_pdf(square_parcel, tmp_path):
    out = tmp_path / "flat.pdf"
    scale = render_flat_map(
        square_parcel, out, features_geojson=_features_near(square_parcel),
        address="123 Test Rd, Maryville, TN", county="blount",
    )
    assert out.exists() and _is_pdf(out)
    assert out.stat().st_size > 3000
    assert scale.feet_per_inch == 40


def test_elevation_map_writes_pdf(square_parcel, tmp_path):
    out = tmp_path / "elev.pdf"
    render_elevation_map(square_parcel, out, address="123 Test Rd", county="blount")
    assert out.exists() and _is_pdf(out)
    assert out.stat().st_size > 3000
