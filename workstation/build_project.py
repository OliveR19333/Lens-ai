"""
Build the TNC-GAS base QGIS project automatically.

Run INSIDE QGIS (Plugins -> Python Console):

    exec(open('/Users/ryanolive/TNC-GAS/tools/build_project.py').read())

Loads, for all four counties: parcels (yellow outline, labeled with parcel # +
acreage), streets, and water — over an Esri satellite basemap — then saves the
project to ~/TNC-GAS/templates/TNC-base.qgz.
"""
import os

from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol,
                       QgsLineSymbol, QgsPalLayerSettings, QgsTextFormat,
                       QgsTextBufferSettings, QgsVectorLayerSimpleLabeling)

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, "TNC-GAS", "county-data")
COUNTIES = {
    "Blount": "blount/Blount",
    "Loudon": "loudon/Loudon",
    "Monroe": "monroe/Monroe",
    "Sevier": "sevier/Sevier",
}

proj = QgsProject.instance()
proj.clear()

esri = ("type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0")
sat = QgsRasterLayer(esri, "Esri Imagery", "wms")
if sat.isValid():
    proj.addMapLayer(sat)
    print("Added satellite basemap.")


def add_vector(path, name, symbol=None):
    lyr = QgsVectorLayer(path, name, "ogr")
    if not lyr.isValid():
        print("  (skip, not found:", name + ")")
        return None
    if symbol is not None:
        lyr.renderer().setSymbol(symbol)
    proj.addMapLayer(lyr)
    return lyr


def label_parcels(lyr):
    s = QgsPalLayerSettings()
    # Parcel number on top line, acreage below.
    s.fieldName = 'concat("GISLINK", char(10), round("CALC_ACRE", 2), \' ac\')'
    s.isExpression = True
    fmt = QgsTextFormat()
    fmt.setSize(9)
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(1.0)
    fmt.setBuffer(buf)
    s.setFormat(fmt)
    # Only show labels when zoomed in to a property (keeps county view fast/clean).
    s.scaleVisibility = True
    s.minimumScale = 12000
    s.maximumScale = 1
    lyr.setLabeling(QgsVectorLayerSimpleLabeling(s))
    lyr.setLabelsEnabled(True)
    lyr.triggerRepaint()


for name, rel in COUNTIES.items():
    folder = os.path.join(BASE, rel)
    add_vector(os.path.join(folder, "HydroP.shp"), name + " Water",
               QgsFillSymbol.createSimple({"color": "0,120,200,70",
                                           "outline_color": "0,90,160,255",
                                           "outline_width": "0.2"}))
    add_vector(os.path.join(folder, "Streets.shp"), name + " Streets",
               QgsLineSymbol.createSimple({"color": "255,255,255,160", "width": "0.2"}))
    parcels = add_vector(os.path.join(folder, "Parcels.shp"), name + " Parcels",
                         QgsFillSymbol.createSimple({"color": "255,255,0,0",
                                                     "outline_color": "255,255,0,255",
                                                     "outline_width": "0.3"}))
    if parcels is not None:
        label_parcels(parcels)
        print("Added", name, "(parcels + streets + water)")

out = os.path.join(HOME, "TNC-GAS", "templates", "TNC-base.qgz")
os.makedirs(os.path.dirname(out), exist_ok=True)
proj.write(out)
print(f"\nSAVED to: {out}")
print("Zoom into a property to see parcel # + acreage labels.")
