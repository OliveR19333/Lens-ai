"""
Generate the two print-ready PDFs for a job — run in the QGIS Python Console:

    exec(open('/Users/ryanolive/TNC-GAS/tools/make_prints.py').read())
    make_prints('~/TNC-GAS/jobs/2026/mike-white-210')

Renders in Tennessee State Plane (EPSG:2274, US feet) so scale/grid are exact.
  1. site-plan.pdf  — grayscale aerial + black measurement grid + scale bar + north
  2. topo.pdf       — 1-ft contour lines (labeled in feet) over the aerial
Both letter-landscape at a rounded engineering scale (1 in = N ft).
"""
import os

import processing
from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, QgsPrintLayout,
                       QgsLayoutItemMap, QgsLayoutItemScaleBar, QgsLayoutItemLabel,
                       QgsLayoutItemPicture, QgsUnitTypes, QgsLayoutExporter,
                       QgsApplication, QgsLineSymbol, QgsVectorLayerSimpleLabeling,
                       QgsPalLayerSettings, QgsTextFormat, QgsLayoutItemPage,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                       QgsHueSaturationFilter)
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import QRectF

TN = QgsCoordinateReferenceSystem("EPSG:2274")  # Tennessee State Plane, US feet
ENG = [10, 20, 30, 40, 50, 60, 100, 200, 300, 400, 500]  # feet per inch
FRAME = (8, 22, 262, 165)  # map frame on the page (mm): x, y, w, h


def _ftin(w_ft, h_ft):
    fpi = max(w_ft / (FRAME[2] / 25.4), h_ft / (FRAME[3] / 25.4))
    for s in ENG:
        if s >= fpi:
            return s
    return ENG[-1]


def _north():
    for b in QgsApplication.svgPaths():
        for n in ("arrows/NorthArrow_02.svg", "arrows/NorthArrow_04.svg"):
            p = os.path.join(b, n)
            if os.path.exists(p):
                return p
    return None


def _map(lay, layers, ext, ftin):
    m = QgsLayoutItemMap(lay)
    m.attemptSetSceneRect(QRectF(*FRAME))
    m.setCrs(TN)
    m.setLayers(layers)
    m.zoomToExtent(ext)
    m.setScale(ftin * 12.0)
    m.setFrameEnabled(True)
    lay.addLayoutItem(m)
    return m


def _furniture(lay, m, title, sub, ftin):
    t = QgsLayoutItemLabel(lay)
    t.setText(title); t.setFont(QFont("Helvetica", 16))
    t.attemptSetSceneRect(QRectF(8, 5, 250, 8)); lay.addLayoutItem(t)
    s = QgsLayoutItemLabel(lay)
    s.setText(f"{sub}    |    Scale: 1 in = {ftin} ft    |    North up")
    s.setFont(QFont("Helvetica", 9))
    s.attemptSetSceneRect(QRectF(8, 14, 260, 6)); lay.addLayoutItem(s)
    sb = QgsLayoutItemScaleBar(lay)
    sb.setLinkedMap(m); sb.setStyle("Single Box")
    sb.setUnits(QgsUnitTypes.DistanceFeet); sb.setUnitLabel("ft")
    sb.setUnitsPerSegment(ftin); sb.setNumberOfSegments(4); sb.setNumberOfSegmentsLeft(0)
    sb.attemptSetSceneRect(QRectF(8, 190, 90, 12)); lay.addLayoutItem(sb)
    na = _north()
    if na:
        p = QgsLayoutItemPicture(lay); p.setPicturePath(na)
        p.attemptSetSceneRect(QRectF(250, 168, 18, 18)); lay.addLayoutItem(p)


def _pdf(lay, f):
    QgsLayoutExporter(lay).exportToPdf(f, QgsLayoutExporter.PdfExportSettings())
    print("Wrote", f)


def _page(lay, name):
    lay.initializeDefaults(); lay.setName(name)
    try:
        lay.pageCollection().pages()[0].setPageSize("Letter", QgsLayoutItemPage.Landscape)
    except Exception as e:  # noqa: BLE001
        print("(page size:", e, ")")


def make_prints(folder):
    folder = os.path.expanduser(folder)
    mapdir = os.path.join(folder, "map")
    op = os.path.join(mapdir, "orthophoto.tif")
    dp = os.path.join(mapdir, "dsm.tif")
    if not os.path.exists(op):
        print("No orthophoto.tif in", mapdir); return
    proj = QgsProject.instance()

    ortho = QgsRasterLayer(op, "Orthophoto")
    proj.addMapLayer(ortho, False)
    # Desaturate to grayscale for the B/W engineering look.
    try:
        hs = QgsHueSaturationFilter(); hs.setSaturation(-100)
        ortho.pipe().set(hs); ortho.triggerRepaint()
    except Exception as e:  # noqa: BLE001
        print("(grayscale skipped:", e, ")")

    tr = QgsCoordinateTransform(ortho.crs(), TN, proj)
    ext = tr.transformBoundingBox(ortho.extent())
    ftin = _ftin(ext.width(), ext.height())
    print(f"Property ~{int(ext.width())} x {int(ext.height())} ft  ->  scale 1 in = {ftin} ft")

    parcels = None
    for l in proj.mapLayers().values():
        if l.name().endswith("Parcels"):
            parcels = l; break

    # ---- Sheet 1: Site Plan (grayscale aerial + black grid) ----
    lay1 = QgsPrintLayout(proj); _page(lay1, "Site Plan")
    m1 = _map(lay1, [x for x in (parcels, ortho) if x], ext, ftin)
    g = m1.grid(); g.setEnabled(True)
    g.setIntervalX(ftin); g.setIntervalY(ftin)   # 1 grid square = 1 inch on paper
    try:
        g.setLineSymbol(QgsLineSymbol.createSimple({"color": "0,0,0,180", "width": "0.15"}))
    except Exception:
        pass
    g.setAnnotationEnabled(False)
    _furniture(lay1, m1, "SITE PLAN - " + os.path.basename(folder), f"Grid = {ftin} ft", ftin)
    _pdf(lay1, os.path.join(mapdir, "site-plan.pdf"))

    # ---- Sheet 2: Topo (contours over aerial) ----
    contours = None
    if os.path.exists(dp):
        try:
            out = os.path.join(mapdir, "contours.gpkg")
            processing.run("gdal:contour", {"INPUT": dp, "BAND": 1, "INTERVAL": 0.3048,
                                            "FIELD_NAME": "ELEV", "OUTPUT": out})
            c = QgsVectorLayer(out, "Contours (1 ft)", "ogr")
            if c.isValid():
                proj.addMapLayer(c, False)
                c.renderer().setSymbol(QgsLineSymbol.createSimple({"color": "170,60,0,255", "width": "0.3"}))
                s = QgsPalLayerSettings(); s.fieldName = 'round("ELEV" / 0.3048)'
                s.isExpression = True; s.placement = QgsPalLayerSettings.Line
                tf = QgsTextFormat(); tf.setSize(7); s.setFormat(tf)
                c.setLabeling(QgsVectorLayerSimpleLabeling(s)); c.setLabelsEnabled(True)
                contours = c
        except Exception as e:  # noqa: BLE001
            print("(contours skipped:", e, ")")

    lay2 = QgsPrintLayout(proj); _page(lay2, "Topo")
    m2 = _map(lay2, [x for x in (contours, ortho) if x], ext, ftin)
    _furniture(lay2, m2, "TOPOGRAPHY - " + os.path.basename(folder),
               "Contours: 1 ft interval (labels in ft)", ftin)
    _pdf(lay2, os.path.join(mapdir, "topo.pdf"))

    print("\nDone. site-plan.pdf and topo.pdf in:", mapdir)


print("Ready. Use:  make_prints('~/TNC-GAS/jobs/2026/mike-white-210')")
