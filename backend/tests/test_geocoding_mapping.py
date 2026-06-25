"""Tests for geocoding helpers that don't require network access."""
from app.services.geocoding import SUPPORTED_COUNTIES, _normalize_county


def test_supported_counties_match_spec():
    assert set(SUPPORTED_COUNTIES) == {"blount", "knox", "sevier"}


def test_normalize_known_county():
    key, disp = _normalize_county("Blount County")
    assert key == "blount"
    assert disp == "Blount County"


def test_normalize_is_case_insensitive():
    key, _ = _normalize_county("KNOX COUNTY")
    assert key == "knox"


def test_normalize_unsupported_county_returns_raw_name():
    key, disp = _normalize_county("Loudon County")
    assert key is None
    assert disp == "Loudon County"


def test_normalize_none():
    assert _normalize_county(None) == (None, None)
