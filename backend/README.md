# GAS Property Mapping — Backend (FastAPI)

Python 3.11 / FastAPI backend for the GAS Property Mapping System. Implements the
API surface in [spec §4.2](../docs/TECH_SPEC.md#42-api-endpoints).

## Layout

```
app/
├── main.py            FastAPI app + router wiring
├── config.py          Settings (pydantic-settings / .env)
├── auth.py            JWT auth (PyJWT)
├── database.py        SQLAlchemy engine/session (PostGIS)
├── models.py          ORM models (Project, CountyCache)
├── schemas.py         Pydantic request/response models
├── storage.py         Artifact storage (local FS / S3-swap point)
├── routers/           auth, counties, geocode, parcels, missions, projects, sync
├── services/
│   ├── geocoding.py        US Census + Google fallback        ✅ implemented
│   ├── parcels.py          PostGIS point-in-polygon lookup    ✅ implemented
│   ├── mission/            DJI WPML 2.0 KMZ builder           ✅ implemented + tested
│   │   ├── geo.py              local-plane geodesy (feet)
│   │   ├── grid.py             lawnmower flight-line planner
│   │   ├── wpml.py             WPML/KML XML builders
│   │   └── kmz_builder.py      assemble the .kmz archive
│   ├── maps/
│   │   ├── scale.py            print-scale calculation        ✅ implemented + tested
│   │   ├── layout.py           page-layout math               ✅ implemented + tested
│   │   ├── render_common.py    shared cartographic drawing    ✅ implemented
│   │   ├── flat_map.py         Map 1 renderer (matplotlib)     ✅ implemented + tested
│   │   └── elevation_map.py    Map 2 renderer (matplotlib)     ✅ implemented + tested
│   ├── webodm.py           WebODM REST client                  ✅ implemented + tested
│   ├── feature_detection.py AI detection entry point           ✅ implemented + tested
│   └── detection/          tiling · geotransform · merge/NMS ·
│                           spectral water · slope · pipeline    ✅ implemented + tested
├── gis/
│   ├── arcgis.py          ArcGIS REST paginated downloader     ✅ implemented + tested
│   ├── normalize.py       parcel attribute normalization       ✅ implemented + tested
│   ├── bundle.py          gzip bundle + version hash           ✅ implemented + tested
│   └── county_sync.py     orchestration (download→bundle)       ✅ implemented*
└── workers/               Celery app + tasks (monthly sync)     ⚙ stub orchestration
```

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit secrets
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080/docs for interactive Swagger UI.

## Test

The pure-logic modules (KMZ builder, flight grid, print scale, county mapping)
have **no third-party dependencies** and run standalone:

```bash
pip install pytest
python -m pytest tests/ -q
```

## What's real vs. stubbed

| Component | Status |
|-----------|--------|
| JWT auth, routers, schemas, models | ✅ implemented |
| Geocoding (US Census + Google fallback) | ✅ implemented |
| DJI WPML 2.0 KMZ mission builder | ✅ implemented + tested |
| Flight-grid + print-scale math | ✅ implemented + tested |
| PostGIS parcel lookup SQL | ✅ implemented (needs synced data) |
| County GIS sync (ArcGIS → normalize → gzip bundle) | ✅ implemented* |
| Map rendering — flat + elevation PDFs (matplotlib) | ✅ implemented + tested |
| WebODM client — auth → task → poll → ortho/DEM download | ✅ implemented + tested |
| AI feature detection (tiling → YOLOv8 → NMS → water + slope) | ✅ implemented + tested* |

\* County sync is fully implemented end-to-end; each county's ArcGIS service URL
must still be **verified and filled in** (`gis/county_sync.py`, spec §5.1) before
automated download works. Until then, load parcels via the PWA's manual import.

Map rendering works from just a parcel boundary (scaled grid sheet); the
orthomosaic/hillshade/contour layers activate when WebODM GeoTIFFs + `rasterio`
are present.

\* AI feature detection: the full pipeline (tiling, NMS/merge, georeferencing,
spectral water, slope) is implemented and unit-tested. The YOLOv8 object-
detection stage needs a **trained aerial model** (`YOLO_MODEL_PATH`, spec
§14.3 — pick one from Roboflow Universe); without it, spectral water + slope
still run and detection degrades gracefully to an empty/partial collection
rather than failing.
