"""
Measurement layers for QGIS — dimensions that stay on the map and print.

    exec(open('/Users/ryanolive/TNC-GAS/tools/measure.py').read())
    measure_line()   # draw lines; each auto-labels its length in feet
    measure_area()   # draw shapes; each auto-labels its area in square feet

Left-click to place points, double-click (or right-click) to finish a shape.
Everything is measured in Tennessee State Plane (US feet) for accuracy.
"""
from qgis.core import (QgsProject, QgsVectorLayer, QgsPalLayerSettings, QgsTextFormat,
                       QgsTextBufferSettings, QgsVectorLayerSimpleLabeling,
                       QgsLineSymbol, QgsFillSymbol)
from qgis.utils import iface


def _new(kind, name, expr, symbol):
    proj = QgsProject.instance()
    for lyr in proj.mapLayersByName(name):
        proj.removeMapLayer(lyr)
    vl = QgsVectorLayer(f"{kind}?crs=EPSG:2274", name, "memory")
    s = QgsPalLayerSettings()
    s.fieldName = expr
    s.isExpression = True
    if kind == "LineString":
        s.placement = QgsPalLayerSettings.Line
    tf = QgsTextFormat(); tf.setSize(11)
    buf = QgsTextBufferSettings(); buf.setEnabled(True); buf.setSize(1.2)
    tf.setBuffer(buf); s.setFormat(tf)
    vl.setLabeling(QgsVectorLayerSimpleLabeling(s)); vl.setLabelsEnabled(True)
    vl.renderer().setSymbol(symbol)
    proj.addMapLayer(vl)
    vl.startEditing()
    iface.setActiveLayer(vl)
    try:
        iface.actionAddFeature().trigger()
    except Exception:  # noqa: BLE001
        pass
    return vl


def measure_line():
    _new("LineString", "Measurements (length)",
         "round(length($geometry), 1) || ' ft'",
         QgsLineSymbol.createSimple({"color": "255,0,0", "width": "0.6"}))
    print("Draw lines — each shows its length in FEET. Double-click to finish a line.")


def measure_area():
    _new("Polygon", "Measurements (area)",
         "round(area($geometry)) || ' sq ft'",
         QgsFillSymbol.createSimple({"color": "255,0,0,40", "outline_color": "255,0,0,255",
                                     "outline_width": "0.5"}))
    print("Draw shapes — each shows its area in SQUARE FEET. Double-click to close a shape.")


print("Ready.  measure_line()  for distances,  measure_area()  for square footage.")
