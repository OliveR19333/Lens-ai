"""
Find a property by street address inside QGIS.

Run once per QGIS session (Plugins -> Python Console):

    exec(open('/Users/ryanolive/TNC-GAS/tools/find_address.py').read())

Then jump to any address:

    find("123 Main St, Maryville, TN")

Geocodes the address (US Census, then OpenStreetMap as a fallback), zooms the map
to it, and drops a red pin. The parcel under the pin is the property.
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
        print("(census lookup failed:", exc, ")")
    try:
        qs = urllib.parse.urlencode({"q": address, "format": "json", "limit": "1"})
        req = urllib.request.Request("https://nominatim.openstreetmap.org/search?" + qs,
                                     headers={"User-Agent": "TNC-GAS/1.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if d:
            return float(d[0]["lat"]), float(d[0]["lon"]), d[0].get("display_name", address)
    except Exception as exc:  # noqa: BLE001
        print("(osm lookup failed:", exc, ")")
    return None


def find(address):
    hit = _geocode(address)
    if not hit:
        print("No location found for:", address)
        return
    lat, lon, matched = hit
    print("Found:", matched)
    proj = QgsProject.instance()
    dest = proj.crs()
    tr = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), dest, proj)
    pt = tr.transform(QgsPointXY(lon, lat))
    canvas = iface.mapCanvas()
    canvas.setCenter(pt)
    canvas.zoomScale(1500)
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
    print("Zoomed in — the parcel under the red pin is your property.")


print("Ready. Find a property with, e.g.:  find('123 Main St, Maryville, TN')")
