# TNC-GAS — Local Mapping Workstation

Processing and GIS run **locally on the Mac** (M-series, 48GB). The cloud side
(`tnc-gas` server) is kept for the lightweight web half and repurposed later.

## Local ⇄ Cloud split

| Job | Where | Why |
|-----|-------|-----|
| Photogrammetry (video → orthomosaic + elevation) | **Local** (WebODM on the Mac) | Heavy, free, fast, private |
| GIS measure / parcel overlay / print | **Local** (QGIS) | Pro tooling, offline |
| County parcel data | **Local** (`county-data/`) + cloud copy | Survey reference |
| Address → parcel lookup, client sharing | **Cloud** (`tnc-gas`, later) | Light, always-on |

## Reference folder (`~/TNC-GAS/`)

```
TNC-GAS/
  county-data/   county parcel shapefiles (Blount, Loudon, Monroe, Sevier)
  jobs/2026/     one folder per property: video, frames, ortho, dsm, final PDF
  tools/         processing scripts (tnc_process.py)
  templates/     QGIS project + print-layout templates
  outputs/       finished maps / client PDFs
```

## Per-property workflow

1. Fly the lot manually, camera straight down, **video + `.SRT`** (subtitles on).
2. Drop the video in a new `jobs/2026/<address>/` folder.
3. Extract frames + stamp GPS from the `.SRT`, then process in WebODM → ortho + elevation.
4. Open in QGIS with the **county parcel boundary** overlaid; measure + mark up.
5. Print to scale / export PDF → `outputs/` (and Drive).
