"""
Generate the two print-ready PDFs for a job — run in the QGIS Python Console:

    exec(open('/Users/ryanolive/TNC-GAS/tools/make_prints.py').read())
    make_prints('~/TNC-GAS/jobs/2026/mike-white-210')

Produces, in <job>/map/:
  1. site-plan.pdf  — orthophoto, measurement grid, scale bar, north arrow, parcel line
  2. topo.pdf       — contour lines (labeled in feet) over the imagery, scale bar, north arrow

Both letter-landscape at a rounded engineering scale (1 in = N ft). Print layouts
are fiddly — expect to fine-tune scale/grid/contour spacing after the first look.
"""
import math
import os

import processing
from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, QgsPrintLayout,
                       QgsLayoutItemMap, QgsLayoutItemScaleBar, QgsLayoutItemLabel,
                       QgsLayoutItemPicture, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes,
                       QgsLayoutExporter, QgsApplication, QgsLineSymbol,
                       QgsVectorLayerSimpleLabeling, QgsPalLayerSettings, QgsTextFormat,
                       QgsLayoutItemPage)
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import QRectF

M_PER_FT = 0.3048
ENG_SCALES = [10, 20, 30, 40, 50, 60, 100, 200, 300, 400, 500]  # feet per inch


def _round_scale(width_m, height_m, frame_w_mm, frame_h_mm):
    denom = max(width_m * 1000.0 / frame_w_mm, height_m * 1000.0 / frame_h_mm)
    ft_per_in = denom / 12.0
    for s in ENG_SCALES:
        if s >= ft_per_in:
            return s
    return ENG_SCALES[-1]


def _north_arrow_path():
    for base in QgsApplication.svgPaths():
        for name in ("arrows/NorthArrow_02.svg", "arrows/NorthArrow_04.svg", "wind_roses/WindRose_01.svg"):
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
    return None


def _base_map(layout, layers, extent, scale):
    m = QgsLayoutItemMap(layout)
    m.attemptSetSceneRect(QRectF(8, 22, 262, 165))  # mm
    m.setLayers(layers)
    m.zoomToExtent(extent)
    m.setScale(scale * 12 * 0.0254 * 39.3701)  # ft/in -> 1:denom (denom = ft/in*12)
    m.setScale(scale * 12.0)
    m.setFrameEnabled(True)
    layout.addLayoutItem(m)
    return m


def _add_furniture(layout, m, title, subtitle, scale_ftin):
    # Title
    t = QgsLayoutItemLabel(layout)
    t.setText(title)
    t.attemptSetSceneRect(QRectF(8, 6, 200, 8))
    from qgis.PyQt.QtGui import QFont
    t.setFont(QFont("Helvetica", 16))
    layout.addLayoutItem(t)
    # Subtitle / scale note
    s = QgsLayoutItemLabel(layout)
    s.setText(f"{subtitle}    |    Scale: 1 in = {scale_ftin} ft    |    North ↑")
    s.attemptSetSceneRect(QRectF(8, 14, 260, 6))
    s.setFont(QFont("Helvetica", 9))
    layout.addLayoutItem(s)
    # Scale bar (feet)
    sb = QgsLayoutItemScaleBar(layout)
    sb.setLinkedMap(m)
    sb.setStyle("Single Box")
    sb.setUnits(QgsUnitTypes.DistanceFeet)
    sb.setUnitLabel("ft")
    sb.setUnitsPerSegment(scale_ftin * 2)
    sb.setNumberOfSegments(4)
    sb.setNumberOfSegmentsLeft(0)
    sb.attemptSetSceneRect(QRectF(8, 190, 90, 12))
    layout.addLayoutItem(sb)
    # North arrow
    na = _north_arrow_path()
    if na:
        pic = QgsLayoutItemPicture(layout)
        pic.setPicturePath(na)
        pic.attemptSetSceneRect(QRectF(250, 168, 18, 18))
        layout.addLayoutItem(pic)


def _export(layout, pdf):
    exp = QgsLayoutExporter(layout)
    exp.exportToPdf(pdf, QgsLayoutExporter.PdfExportSettings())
    print("Wrote", pdf)


def make_prints(folder):
    folder = os.path.expanduser(folder)
    mapdir = os.path.join(folder, "map")
    ortho_p = os.path.join(mapdir, "orthophoto.tif")
    dsm_p = os.path.join(mapdir, "dsm.tif")
    if not os.path.exists(ortho_p):
        print("No orthophoto.tif in", mapdir)
        return
    proj = QgsProject.instance()

    ortho = QgsRasterLayer(ortho_p, "Orthophoto")
    proj.addMapLayer(ortho, False)
    ext = ortho.extent()
    scale_ftin = _round_scale(ext.width(), ext.height(), 262, 165)
    denom = scale_ftin * 12.0

    # Parcel layer already in project (if TNC-base loaded); grab the first "Parcels".
    parcels = None
    for lyr in proj.mapLayers().values():
        if lyr.name().endswith("Parcels"):
            parcels = lyr
            break

    # ---- Sheet 1: Site Plan (flat) with grid ----
    lay1 = QgsPrintLayout(proj)
    lay1.initializeDefaults()
    lay1.setName("Site Plan")
    lay1.pageCollection().pages()[0].setPageSize("Letter", QgsLayoutItemPage.Landscape)
    layers1 = [parcels, ortho] if parcels else [ortho]
    m1 = _base_map(lay1, [l for l in layers1 if l], ext, scale_ftin)
    # measurement grid: one square = 1 inch on paper = scale_ftin feet
    grid = m1.grid()
    grid.setEnabled(True)
    grid.setIntervalX(scale_ftin * M_PER_FT)
    grid.setIntervalY(scale_ftin * M_PER_FT)
    grid.setStyle(grid.Solid if hasattr(grid, "Solid") else 0)
    try:
        gsym = QgsLineSymbol.createSimple({"color": "255,255,255,120", "width": "0.15"})
        grid.setLineSymbol(gsym)
    except Exception:
        pass
    grid.setAnnotationEnabled(False)
    _add_furniture(lay1, m1, "SITE PLAN — " + os.path.basename(folder),
                   f"Grid = {scale_ftin} ft", scale_ftin)
    _export(lay1, os.path.join(mapdir, "site-plan.pdf"))

    # ---- Sheet 2: Topo with contours ----
    contours = None
    if os.path.exists(dsm_p):
        try:
            out = os.path.join(mapdir, "contours.gpkg")
            processing.run("gdal:contour", {
                "INPUT": dsm_p, "BAND": 1, "INTERVAL": M_PER_FT,  # 1-ft contours
                "FIELD_NAME": "ELEV", "OUTPUT": out})
            contours = QgsVectorLayer(out, "Contours (1 ft)", "ogr")
            if contours.isValid():
                proj.addMapLayer(contours, False)
                contours.renderer().setSymbol(
                    QgsLineSymbol.createSimple({"color": "150,75,0,255", "width": "0.25"}))
                # label contours in FEET
                s = QgsPalLayerSettings()
                s.fieldName = 'round("ELEV" / 0.3048)'
                s.isExpression = True
                s.placement = QgsPalLayerSettings.Line
                tf = QgsTextFormat(); tf.setSize(7)
                s.setFormat(tf)
                contours.setLabeling(QgsVectorLayerSimpleLabeling(s))
                contours.setLabelsEnabled(True)
            else:
                contours = None
        except Exception as exc:  # noqa: BLE001
            print("(contours skipped:", exc, ")")

    lay2 = QgsPrintLayout(proj)
    lay2.initializeDefaults()
    lay2.setName("Topo")
    lay2.pageCollection().pages()[0].setPageSize("Letter", QgsLayoutItemPage.Landscape)
    layers2 = [c for c in (contours, ortho) if c]
    m2 = _base_map(lay2, layers2, ext, scale_ftin)
    _add_furniture(lay2, m2, "TOPOGRAPHY — " + os.path.basename(folder),
                   "Contours: 1 ft interval (labels in ft)", scale_ftin)
    _export(lay2, os.path.join(mapdir, "topo.pdf"))

    print("\nDone. Two PDFs in:", mapdir)
    print("  site-plan.pdf  and  topo.pdf")


print("Ready. Use:  make_prints('~/TNC-GAS/jobs/2026/mike-white-210')")
