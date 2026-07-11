"""Tests for the county GIS sync pipeline (spec §5.2): ArcGIS pagination,
attribute normalization, and bundle packaging. All offline (fetch injected)."""
import gzip
import json

from app.gis import arcgis, bundle, normalize


def _feature(pid, lng=-83.97, lat=35.75):
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [[[lng, lat], [lng + 0.001, lat],
                     [lng + 0.001, lat + 0.001], [lng, lat + 0.001], [lng, lat]]]},
        "properties": {"PARCELID": pid, "OWNER": f"Owner {pid}", "SITEADDR": f"{pid} Main St"},
    }


# ---- ArcGIS pagination ----
def test_pagination_stops_on_short_page():
    pages = {0: [_feature(i) for i in range(1000)], 1000: [_feature(i) for i in range(1000, 1500)]}

    def fake_fetch(url):
        # Parse resultOffset from the URL.
        import urllib.parse as up
        q = up.parse_qs(up.urlparse(url).query)
        offset = int(q["resultOffset"][0])
        return {"type": "FeatureCollection", "features": pages.get(offset, [])}

    fc = arcgis.fetch_layer_geojson("http://x/0", page_size=1000, fetch=fake_fetch)
    assert len(fc["features"]) == 1500


def test_pagination_respects_exceeded_transfer_limit_flag():
    calls = {"n": 0}

    def fake_fetch(url):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"features": [_feature(i) for i in range(2)], "exceededTransferLimit": True}
        return {"features": [_feature(99)]}  # short page, no flag → stop

    fc = arcgis.fetch_layer_geojson("http://x", page_size=2, fetch=fake_fetch)
    assert len(fc["features"]) == 3


def test_max_features_caps_download():
    def fake_fetch(url):
        return {"features": [_feature(i) for i in range(1000)], "exceededTransferLimit": True}

    fc = arcgis.fetch_layer_geojson("http://x", page_size=1000, max_features=2500, fetch=fake_fetch)
    assert len(fc["features"]) == 2500


def test_query_url_has_geojson_and_offset():
    url = arcgis.build_query_url("http://x/FeatureServer/0", offset=50, page_size=10)
    assert "f=geojson" in url
    assert "resultOffset=50" in url
    assert "/query?" in url


# ---- Normalization ----
def test_normalize_maps_alias_fields():
    fc = {"type": "FeatureCollection", "features": [_feature("123")]}
    out = normalize.normalize_collection(fc, "blount")
    p = out["features"][0]["properties"]
    assert p["parcel_id"] == "123"
    assert p["owner"] == "Owner 123"
    assert p["address"] == "123 Main St"
    assert p["county"] == "blount"


def test_normalize_is_case_insensitive():
    feat = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]},
            "properties": {"parcelid": "x", "ownername": "Jane"}}
    out = normalize.normalize_feature(feat, "knox")
    assert out["properties"]["parcel_id"] == "x"
    assert out["properties"]["owner"] == "Jane"


def test_normalize_drops_geometryless_features():
    fc = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": None, "properties": {"PIN": "1"}},
        _feature("2"),
    ]}
    out = normalize.normalize_collection(fc, "sevier")
    assert len(out["features"]) == 1


# ---- Bundle packaging ----
def test_bundle_hash_is_stable_and_order_independent():
    fc1 = {"type": "FeatureCollection", "features": [_feature("a"), _feature("b")]}
    h1 = bundle.version_hash(fc1)
    h2 = bundle.version_hash(json.loads(json.dumps(fc1)))
    assert h1 == h2 and len(h1) == 16


def test_bundle_gzip_roundtrips(tmp_path):
    fc = {"type": "FeatureCollection", "features": [_feature(i) for i in range(20)]}
    result = bundle.package_bundle("blount", fc, data_dir=tmp_path)
    assert result.parcel_count == 20
    assert result.gzip_bytes < result.raw_bytes
    gz_bytes, version = bundle.read_bundle("blount", tmp_path)
    restored = json.loads(gzip.decompress(gz_bytes))
    assert len(restored["features"]) == 20
    assert version == result.version_hash
