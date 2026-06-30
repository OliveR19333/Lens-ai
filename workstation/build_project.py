"""
Build the TNC-GAS base QGIS project automatically.

Run this INSIDE QGIS (Plugins -> Python Console), with:

    exec(open('/Users/ryanolive/TNC-GAS/tools/build_project.py').read())

It loads the four county parcel layers + an Esri satellite basemap, styles the
parcels as transparent fill with a yellow outline, and saves the project to
~/TNC-GAS/templates/TNC-base.qgz. Open that file to get everything back instantly.
"""
import os

from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, "TNC-GAS", "county-data")
COUNTIES = {
    "Blount": "blount/Blount/Parcels.shp",
    "Loudon": "loudon/Loudon/Parcels.shp",
    "Monroe": "monroe/Monroe/Parcels.shp",
    "Sevier": "sevier/Sevier/Parcels.shp",
}

proj = QgsProject.instance()
proj.clear()

# Esri World Imagery satellite basemap (XYZ tiles, no key needed).
esri = ("type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0")
sat = QgsRasterLayer(esri, "Esri Imagery", "wms")
if sat.isValid():
    proj.addMapLayer(sat)
    print("Added satellite basemap.")
else:
    print("WARNING: satellite basemap failed to load (check internet).")

# County parcels: transparent fill + yellow outline so satellite shows through.
loaded = 0
for name, rel in COUNTIES.items():
    path = os.path.join(BASE, rel)
    lyr = QgsVectorLayer(path, name + " Parcels", "ogr")
    if not lyr.isValid():
        print("FAILED to load:", path)
        continue
    sym = QgsFillSymbol.createSimple({
        "color": "255,255,0,0",            # transparent fill
        "outline_color": "255,255,0,255",  # yellow outline
        "outline_width": "0.3",
    })
    lyr.renderer().setSymbol(sym)
    lyr.triggerRepaint()
    proj.addMapLayer(lyr)
    loaded += 1
    print("Added", name, "parcels.")

out = os.path.join(HOME, "TNC-GAS", "templates", "TNC-base.qgz")
os.makedirs(os.path.dirname(out), exist_ok=True)
proj.write(out)
print(f"\nSAVED {loaded} county layers + satellite to:\n  {out}")
print("From now on, just open TNC-base.qgz to get everything back.")
