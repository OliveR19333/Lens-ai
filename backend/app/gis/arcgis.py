"""ArcGIS REST FeatureServer/MapServer downloader (spec §5.2 step 1-2).

Most county GIS portals (including the East TN counties) expose parcels through
an ArcGIS REST service whose ``/query`` endpoint can return GeoJSON directly.
This module pulls an entire layer with offset pagination, since servers cap each
response (``maxRecordCount``, typically 1000-2000 features).

Standard library only (urllib), so it imports without geopandas/GDAL. The HTTP
fetch is injectable so the pagination logic is unit-testable offline.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Callable, Optional

# A fetch callable: (url) -> parsed JSON dict. Default uses urllib.
FetchJson = Callable[[str], dict]


def _default_fetch(url: str, timeout: float = 60.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "GAS-Mapping/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def build_query_url(
    service_url: str,
    *,
    offset: int = 0,
    page_size: int = 1000,
    where: str = "1=1",
    out_fields: str = "*",
    out_sr: int = 4326,
) -> str:
    """Build one ArcGIS ``/query`` request URL returning GeoJSON."""
    base = service_url.rstrip("/")
    if not base.endswith("/query"):
        base = base + "/query"
    params = {
        "where": where,
        "outFields": out_fields,
        "outSR": out_sr,
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": page_size,
        "returnGeometry": "true",
    }
    return f"{base}?{urllib.parse.urlencode(params)}"


def fetch_layer_geojson(
    service_url: str,
    *,
    page_size: int = 1000,
    where: str = "1=1",
    max_features: Optional[int] = None,
    fetch: FetchJson = _default_fetch,
) -> dict:
    """Download an entire ArcGIS layer as one GeoJSON FeatureCollection.

    Pages with ``resultOffset`` until a short page is returned (or
    ``exceededTransferLimit`` clears, or ``max_features`` is reached).
    """
    features: list[dict] = []
    offset = 0
    while True:
        url = build_query_url(service_url, offset=offset, page_size=page_size, where=where)
        data = fetch(url)
        if "error" in data:
            raise RuntimeError(f"ArcGIS error: {data['error']}")
        page = data.get("features", [])
        features.extend(page)
        exceeded = data.get("exceededTransferLimit") or data.get("properties", {}).get(
            "exceededTransferLimit"
        )
        if max_features is not None and len(features) >= max_features:
            features = features[:max_features]
            break
        # Stop when the server returns a partial page and isn't flagging more.
        if len(page) < page_size and not exceeded:
            break
        if not page:
            break
        offset += len(page)
    return {"type": "FeatureCollection", "features": features}
