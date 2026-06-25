# GAS Property Mapping System

Mobile-first workflow that turns a **property address** into a **DJI-compatible
waypoint mission** and, after the flight, into **two print-ready planning maps**
(a flat orthomosaic grid map and an elevation-change map) on a locked,
proportionally-enlargeable scale.

Built for **Guardian Aerial Solutions / TNC** — irrigation system design and
hardscape/landscape construction planning across Blount, Knox, and Sevier
counties (East Tennessee).

> 📄 Full requirements live in [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md)
> (Technical Specification v1.0, June 2026).

---

## What this repo contains

This is a **monorepo scaffold for all four development phases** described in the
spec. Self-contained domain logic (KMZ mission generation, flight-grid
computation, print-scale math, geocoding) is **fully implemented and tested**;
components that depend on external services (WebODM, PostGIS, YOLOv8, county GIS
portals) are **structured stubs** with clear `TODO` markers and the API surface
already wired so they can be filled in phase by phase.

```
.
├── docs/                  Technical spec (markdown) + extracted source text
├── backend/               Python 3.11 / FastAPI backend
│   ├── app/
│   │   ├── main.py            FastAPI app + router wiring
│   │   ├── config.py          Settings (pydantic-settings, .env)
│   │   ├── auth.py            JWT auth helpers
│   │   ├── database.py        SQLAlchemy engine/session (PostGIS)
│   │   ├── models.py          ORM models (Project, County, ...)
│   │   ├── schemas.py         Pydantic request/response models
│   │   ├── routers/          One module per endpoint group (spec §4.2)
│   │   ├── services/
│   │   │   ├── geocoding.py        US Census + Google fallback  ✅ real
│   │   │   ├── parcels.py          PostGIS point-in-polygon lookup
│   │   │   ├── mission/            DJI WPML 2.0 KMZ builder      ✅ real
│   │   │   ├── webodm.py           WebODM REST client            ⚙ stub
│   │   │   ├── feature_detection.py YOLOv8 + spectral water      ⚙ stub
│   │   │   └── maps/               Flat + elevation renderers    ⚙ stub
│   │   ├── gis/               County GIS download → GeoJSON       ⚙ stub
│   │   └── workers/          Celery app + monthly sync beat
│   └── tests/               pytest suite (KMZ, grid, scale)      ✅ runnable
├── pwa/                    React 18 + Vite PWA (Workbox, MapLibre, Zustand)
└── infra/                 docker-compose (Postgres/PostGIS, Redis, WebODM)
```

Legend: ✅ implemented & tested · ⚙ scaffolded stub (TODO).

---

## Quick start

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit secrets
uvicorn app.main:app --reload # http://localhost:8080/docs
```

Run the (dependency-free) domain tests:

```bash
cd backend
python -m pytest tests/ -q     # KMZ builder, flight grid, print scale
```

### PWA (React / Vite)

```bash
cd pwa
npm install
npm run dev                    # http://localhost:5173
npm run build                  # production PWA bundle
```

### Full stack (Docker)

```bash
cd infra
docker compose up -d           # Postgres/PostGIS + Redis + WebODM + backend
```

---

## End-to-end workflow (spec §2)

1. **Mission setup (field, day-of):** enter address → geocode → load cached
   parcel boundary → generate Waypoint KMZ → hand off to DJI Fly via the iOS
   share sheet → fly with the Mini 4 Pro.
2. **Processing (post-flight, WiFi):** upload images to WebODM → orthomosaic +
   DEM → AI feature detection (ponds, trees, structures, driveways).
3. **Map output:** auto-fit print scale → render Map 1 (flat grid) and Map 2
   (elevation) → export print-ready PDFs at a locked, enlargeable scale.

---

## Build order (spec §14.1)

> Start with **Phase 1 MVP only.** Do not build WebODM or AI detection until KMZ
> generation and offline parcel lookup are solid — the operator needs to fly
> within the first sprint.

| Phase | Focus | Status in this scaffold |
|-------|-------|-------------------------|
| 1 — MVP | Address → geocode → parcel → KMZ + offline cache | Core logic implemented |
| 2 — Processing | WebODM upload, ortho/DEM retrieval, flat map | Stubbed |
| 3 — Elevation & features | Contours, slope arrows, AI detection | Stubbed |
| 4 — Polish & scale | More counties, annotation, multi-user | Planned |

---

## Key constraints (spec §14.2)

- **iPhone-first** — PWA installs via Safari iOS only; test every screen there.
- **Offline is non-negotiable** — East TN field sites have poor LTE.
- **DJI Mini 4 Pro** — `droneEnumValue = 67` in WPML 2.0.
- **Map output** — 8.5×11 single sheet, ≥300 DPI, PDF, with scale bar + ratio.
- **All elevation in feet** (US contractor standard).

See [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md) §14.3 for open kickoff questions.
