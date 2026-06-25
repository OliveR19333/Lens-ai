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
│   │   ├── flat_map.py         Map 1 renderer                  ⚙ stub (Phase 2)
│   │   └── elevation_map.py    Map 2 renderer                  ⚙ stub (Phase 3)
│   ├── webodm.py           WebODM REST client                  ⚙ stub (Phase 2)
│   └── feature_detection.py YOLOv8 + spectral water + slope    ⚙ stub (Phase 3)
├── gis/county_sync.py     County GIS download → PostGIS         ⚙ stub
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
| WebODM client, AI detection, map render, GIS sync | ⚙ structured stubs (clear TODOs) |

Stubs raise `NotImplementedError` with a spec reference, or return valid empty
results, so the API stays coherent while Phases 2–3 are filled in.
