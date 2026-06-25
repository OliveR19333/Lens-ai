"""Address geocoding (spec §4.3).

Primary: US Census Geocoder (free, no API key). Fallback: Google Maps Geocoding
(requires ``GOOGLE_MAPS_API_KEY``). After geocoding, the resulting county name
is mapped to one of the supported county enum values (spec §5.1).

Uses the standard library ``urllib`` only, so the module imports cleanly without
third-party HTTP dependencies. Network calls are wrapped so a failure of the
primary provider transparently falls through to the fallback.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

# Supported counties (spec §5.1) keyed by the Project.county enum value.
SUPPORTED_COUNTIES = {
    "blount": "Blount County",
    "knox": "Knox County",
    "sevier": "Sevier County",
}

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
GOOGLE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class GeocodeError(Exception):
    pass


@dataclass
class GeocodeResult:
    address: str            # normalized / matched address
    lat: float
    lng: float
    county: Optional[str]   # enum value: blount|knox|sevier, or None if unsupported
    county_name: Optional[str]
    source: str             # "census" | "google"

    def as_dict(self) -> dict:
        return {
            "address": self.address,
            "lat": self.lat,
            "lng": self.lng,
            "county": self.county,
            "county_name": self.county_name,
            "source": self.source,
        }


def _normalize_county(raw_name: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Map a county name (e.g. 'Blount County') to its enum value, if supported."""
    if not raw_name:
        return None, None
    lowered = raw_name.lower()
    for key, display in SUPPORTED_COUNTIES.items():
        if key in lowered:
            return key, display
    return None, raw_name


def _http_get_json(url: str, timeout: float = 10.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "GAS-Mapping/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted hosts)
        return json.loads(resp.read().decode("utf-8"))


def geocode_census(address: str, benchmark: str = "2020") -> Optional[GeocodeResult]:
    """Geocode via the US Census 'geographies' endpoint (returns county too)."""
    qs = urllib.parse.urlencode(
        {
            "address": address,
            "benchmark": "Public_AR_Current",
            "vintage": f"Census{benchmark}_Current",
            "format": "json",
        }
    )
    data = _http_get_json(f"{CENSUS_URL}?{qs}")
    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        return None
    m = matches[0]
    coords = m["coordinates"]
    county_name = None
    counties = m.get("geographies", {}).get("Counties", [])
    if counties:
        county_name = counties[0].get("NAME") or counties[0].get("BASENAME")
    county_key, county_disp = _normalize_county(county_name)
    return GeocodeResult(
        address=m.get("matchedAddress", address),
        lat=float(coords["y"]),
        lng=float(coords["x"]),
        county=county_key,
        county_name=county_disp,
        source="census",
    )


def geocode_google(address: str, api_key: str) -> Optional[GeocodeResult]:
    """Fallback geocode via Google Maps Geocoding API."""
    if not api_key:
        return None
    qs = urllib.parse.urlencode({"address": address, "key": api_key})
    data = _http_get_json(f"{GOOGLE_URL}?{qs}")
    if data.get("status") != "OK" or not data.get("results"):
        return None
    r = data["results"][0]
    loc = r["geometry"]["location"]
    county_name = None
    for comp in r.get("address_components", []):
        if "administrative_area_level_2" in comp.get("types", []):
            county_name = comp.get("long_name")
            break
    county_key, county_disp = _normalize_county(county_name)
    return GeocodeResult(
        address=r.get("formatted_address", address),
        lat=float(loc["lat"]),
        lng=float(loc["lng"]),
        county=county_key,
        county_name=county_disp,
        source="google",
    )


def geocode(address: str, *, census_benchmark: str = "2020", google_api_key: str = "") -> GeocodeResult:
    """Geocode an address, Census first then Google, raising on total failure."""
    address = address.strip()
    if not address:
        raise GeocodeError("Empty address.")

    try:
        result = geocode_census(address, benchmark=census_benchmark)
        if result:
            return result
    except Exception:  # network / parse error → try fallback
        pass

    try:
        result = geocode_google(address, google_api_key)
        if result:
            return result
    except Exception:
        pass

    raise GeocodeError(f"Could not geocode address: {address!r}")
