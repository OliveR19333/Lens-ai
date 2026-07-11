"""
Find a property by street address inside QGIS.

    exec(open('/Users/ryanolive/TNC-GAS/tools/find_address.py').read())
    find("123 Main St, Maryville, TN")

Geocodes (US Census, then OpenStreetMap fallback), zooms the map to it, and drops
a red pin. Transforms the result into the live map canvas CRS so it lands correctly.
"""
import json
import urllib.parse
import urllib.request

from qgis.core import (QgsProject, QgsPointXY, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsVectorLayer, QgsFeature,
                       QgsGeometry, QgsMarkerSymbol)
from qgis.utils import iface

CENSUS = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"


def _geocode(address):
    try:
        qs = urllib.parse.urlencode({"address": address,
                                     "benchmark": "Public_AR_Current", "format": "json"})
        d = json.loads(urllib.request.urlopen(f"{CENSUS}?{qs}", timeout=30).read())
        m = d.get("result", {}).get("addressMatches", [])
        if m:
            c = m[0]["coordinates"]
            return float(c["y"]), float(c["x"]), m[0].get("matchedAddress", address)
    except Exception as exc:  # noqa: BLE001
        print("(census failed:", exc, ")")
    try:
        qs = urllib.parse.urlencode({"q": address, "format": "json", "limit": "1"})
        req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + qs,
                                     headers={"User-Agent": "TNC-GAS/1.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if d:
            return float(d[0]["lat"]), float(d[0]["lon"]), d[0].get("display_name", address)
    except Exception as exc:  # noqa: BLE001
        print("(osm failed:", exc, ")")
    return None


def find(address):
    hit = _geocode(address)
    if not hit:
        print("No location found for:", address)
        return
    lat, lon, matched = hit
    canvas = iface.mapCanvas()
    dest = canvas.mapSettings().destinationCrs()          # the REAL canvas CRS
    tr = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                dest, QgsProject.instance())
    pt = tr.transform(QgsPointXY(lon, lat))
    print("Found:", matched)
    print("  lat,lon =", round(lat, 6), round(lon, 6),
          "| canvas CRS:", dest.authid(),
          "| map xy:", round(pt.x(), 1), round(pt.y(), 1))
    canvas.setCenter(pt)
    canvas.zoomScale(1500)
    proj = QgsProject.instance()
    for lyr in proj.mapLayersByName("Search Result"):
        proj.removeMapLayer(lyr)
    vl = QgsVectorLayer(f"Point?crs={dest.authid()}", "Search Result", "memory")
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPointXY(pt))
    vl.dataProvider().addFeature(feat)
    vl.renderer().setSymbol(QgsMarkerSymbol.createSimple(
        {"name": "circle", "color": "255,0,0", "size": "4", "outline_color": "white"}))
    proj.addMapLayer(vl)
    canvas.refresh()
    print("Zoomed in — red pin marks the property.")


print("Ready. Example:  find('123 Main St, Maryville, TN')")
