"""Shared pytest fixtures."""
import os
import sys

import pytest

# Make the backend package importable when running `pytest` from backend/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def square_parcel() -> dict:
    """A ~300 ft (E–W) × 400 ft (N–S) parcel near Maryville, TN.

    Built from a known origin so width/height in feet are predictable for the
    scale and grid tests. 300 ft ≈ 0.001088° lng at lat 35.75; 400 ft ≈
    0.001096° lat.
    """
    lng0, lat0 = -83.97, 35.75
    # widths chosen to land close to 300 ft / 400 ft after projection
    dlng = 300.0 / (20902231.0 * 3.141592653589793 / 180.0) / __import__("math").cos(
        __import__("math").radians(lat0)
    )
    dlat = 400.0 / (20902231.0 * 3.141592653589793 / 180.0)
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [lng0, lat0],
                [lng0 + dlng, lat0],
                [lng0 + dlng, lat0 + dlat],
                [lng0, lat0 + dlat],
                [lng0, lat0],
            ]
        ],
    }
