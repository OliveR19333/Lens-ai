"""
Nudge the drone map onto the parcel line — run in the QGIS Python Console:

    exec(open('/Users/ryanolive/TNC-GAS/tools/nudge.py').read())
    nudge(3, -2)     # slide the map 3 ft EAST and 2 ft SOUTH

Positive east = right, positive north = up (negative flips it). The orthophoto
must be loaded in QGIS. Nudges are cumulative — keep going until it lines up
(e.g. nudge(-1, 0) to back off a foot). Shifts feet accurately regardless of the
map's coordinate system.
"""
import os

from osgeo import gdal
from qgis.core import (QgsProject, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsPointXY)
from qgis.utils import iface

TN = QgsCoordinateReferenceSystem("EPSG:2274")  # Tennessee State Plane, US feet


def _find_ortho():
    for lyr in QgsProject.instance().mapLayers().values():
        try:
            if lyr.source().lower().endswith("orthophoto.tif"):
                return lyr
        except Exception:  # noqa: BLE001
            pass
    return None


def nudge(east_ft, north_ft):
    proj = QgsProject.instance()
    lyr = _find_ortho()
    if not lyr:
        print("Load orthophoto.tif into QGIS first, then run nudge().")
        return
    path = lyr.source()
    crs = lyr.crs()
    c = lyr.extent().center()
    to_tn = QgsCoordinateTransform(crs, TN, proj)
    back = QgsCoordinateTransform(TN, crs, proj)
    ctn = to_tn.transform(c)
    sh = back.transform(QgsPointXY(ctn.x() + east_ft, ctn.y() + north_ft))
    ddx, ddy = sh.x() - c.x(), sh.y() - c.y()
    ds = gdal.Open(path, gdal.GA_Update)
    if ds is None:
        print("Could not open the file to edit:", path)
        return
    gt = list(ds.GetGeoTransform())
    gt[0] += ddx
    gt[3] += ddy
    ds.SetGeoTransform(gt)
    ds.FlushCache()
    ds = None
    lyr.reload()
    lyr.triggerRepaint()
    iface.mapCanvas().refreshAllLayers()
    print(f"Moved {east_ft} ft E, {north_ft} ft N. Fine-tune with more nudges (e.g. nudge(-1, 0)).")


print("Ready. Slide the map onto the parcel, e.g.:  nudge(3, -2)   (feet: +E, +N)")
