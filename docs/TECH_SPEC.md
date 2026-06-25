# GAS Property Mapping System — Technical Specification

| | |
|---|---|
| **Version** | 1.0 |
| **Client** | Guardian Aerial Solutions / TNC |
| **Date** | June 2026 |
| **Platform** | Mobile PWA + Python Backend |
| **Prepared For** | Developer Handoff (Claude Code / Dev Team) |

> This is a markdown rendering of the source Word handoff document. The raw
> extracted text is preserved verbatim in
> [`spec-source-extract.txt`](spec-source-extract.txt).

---

## 1. System Overview

The GAS Property Mapping System is a mobile-first Progressive Web App (PWA) that
enables field operators to input a property address on the day of a job,
automatically generate a DJI-compatible Waypoint mission, fly the property, and
produce two scaled planning maps: a flat orthomosaic grid map and an elevation
change map. Both maps print on a single 8.5" × 11" sheet at a locked scale that
can be proportionally enlarged to any size (e.g., 25" × 30" grid paper).

Primary use cases:

- Irrigation system design and layout planning
- TNC hardscape and landscape construction planning

### 1.1 System Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Mobile PWA | React / Vite / Workbox | iPhone-accessible UI, offline-capable |
| Backend API | Python / FastAPI | Parcel data sync, mission generation, map output |
| County GIS Cache | SQLite / GeoJSON | Offline parcel boundary storage |
| Mission Generator | Waypoint OS API / KMZ | DJI Fly-compatible waypoint missions |
| Ortho Processor | WebODM / NodeODM | Orthomosaic + DEM from drone images |
| Feature Detector | YOLOv8 / Roboflow | AI detection of ponds, trees, structures |
| Map Renderer | QGIS Python API / Matplotlib | Scaled B&W grid maps for print |

---

## 2. End-to-End User Workflow

**Phase 1 — Mission Setup (Field, Day-Of)**

1. Open PWA on iPhone (works offline)
2. Enter property address manually
3. System geocodes address → determines county → loads cached parcel boundary
4. Review parcel boundary overlay on map
5. Confirm and generate Waypoint mission file (KMZ)
6. KMZ downloads to phone → loads into DJI Fly app
7. Fly mission with Mini 4 Pro

**Phase 2 — Processing (Post-Flight, WiFi Required)**

1. Upload drone images to WebODM via PWA or desktop
2. WebODM generates orthomosaic (GeoTIFF) + Digital Elevation Model (DEM)
3. Backend runs AI feature detection on orthomosaic
4. System flags: water bodies, tree clusters, structures, driveways

**Phase 3 — Map Output**

1. User selects print scale (auto-calculated to fit 8.5" × 11")
2. Map 1: Flat B&W orthomosaic + parcel boundary + feature labels + grid
3. Map 2: Elevation contour map + slope direction indicators + feature labels
4. Both maps export as print-ready PDF at locked scale with scale bar
5. Scale ratio printed on map for proportional enlargement to 25" × 30" grid paper

---

## 3. Mobile PWA Architecture

### 3.1 Technology Stack

| Concern | Choice |
|---------|--------|
| Framework | React 18 + Vite |
| PWA Engine | Workbox — service worker, offline caching |
| Map Display | MapLibre GL JS (offline vector tiles) |
| State | Zustand |
| Local Storage | IndexedDB (parcel GeoJSON cache) |
| HTTP Client | Axios with offline queue |
| Styling | Tailwind CSS |
| Icons | Lucide React |

### 3.2 PWA Requirements

- Installable on iPhone home screen (Add to Home Screen)
- Service worker caches all app assets for full offline use
- County parcel GeoJSON stored in IndexedDB (up to ~50MB per county)
- Address geocoding cached locally for recently searched addresses
- Offline-first: all mission generation runs client-side when offline
- Auto-sync trigger on WiFi connect: checks for parcel data updates

### 3.3 Screen Flow

| Screen | Purpose |
|--------|---------|
| Login | Username + password, JWT auth, persistent session |
| Home / Dashboard | Recent projects, sync status, county cache status |
| New Mission | Address input → map preview → mission settings → generate |
| Parcel Preview | MapLibre map with parcel boundary overlay, confirm before fly |
| Mission Output | KMZ download button + DJI Fly deep link |
| Upload Images | Post-flight: select images → push to WebODM queue |
| Map Viewer | View flat map and elevation map per project |
| Print / Export | Scale selector → PDF generation → share sheet |
| Settings | County selection, monthly sync schedule, account |

### 3.4 DJI Fly Integration

1. Generate KMZ on backend → return download URL to PWA
2. PWA triggers iOS share sheet with KMZ file
3. User selects "Copy to DJI Fly" or saves to Files app → manually imports

> ⚑ **NOTE:** Full programmatic DJI Fly deep-link integration is not publicly
> documented by DJI. The share sheet approach is the most reliable cross-device
> method. Monitor DJI developer updates for direct app-to-app transfer APIs.

---

## 4. Backend API Specification

### 4.1 Stack

| Concern | Choice |
|---------|--------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | PostgreSQL + PostGIS (spatial queries) |
| Task Queue | Celery + Redis (async WebODM jobs, monthly sync) |
| File Storage | Local filesystem or S3-compatible (GeoTIFFs, PDFs) |
| Auth | JWT (PyJWT) — single user or small team |
| Hosting | VPS (DigitalOcean / Linode) or Mac Mini server |

### 4.2 API Endpoints

| Method + Path | Description | Auth |
|---------------|-------------|------|
| `POST /auth/login` | Returns JWT token | None |
| `GET /counties` | List supported counties + cache status | JWT |
| `POST /geocode` | Address → lat/lng + county detection | JWT |
| `POST /parcel/lookup` | Lat/lng → parcel boundary GeoJSON | JWT |
| `POST /mission/generate` | Parcel GeoJSON → Waypoint KMZ file | JWT |
| `GET /mission/{id}/kmz` | Download generated KMZ file | JWT |
| `POST /project/create` | Create new mapping project | JWT |
| `POST /project/{id}/upload` | Upload drone images to WebODM | JWT |
| `GET /project/{id}/status` | WebODM processing status | JWT |
| `GET /project/{id}/maps` | Return flat map + elevation map PDFs | JWT |
| `POST /project/{id}/features` | Trigger AI feature detection | JWT |
| `GET /sync/parcels` | Manual trigger parcel sync | JWT |

### 4.3 Geocoding Service

Primary: **US Census Geocoder** (free, no key). Fallback: **Google Maps Geocoding**.

```
# Primary: US Census Geocoder (free)
GET https://geocoding.geo.census.gov/geocoder/locations/onelineaddress
  ?address={encoded_address}&benchmark=2020&format=json

# Fallback: Google Maps Geocoding API
GET https://maps.googleapis.com/maps/api/geocode/json
  ?address={encoded_address}&key={GOOGLE_API_KEY}
```

---

## 5. County GIS Parcel Data Integration

### 5.1 Supported Counties

| County | GIS Portal URL | Export Format |
|--------|----------------|---------------|
| Blount County, TN | https://www.blounttn.org/2153/GIS-Mapping | Shapefile / KML |
| Knox County, TN | https://www.knoxplanning.org/gis/ | Shapefile / GeoJSON |
| Sevier County, TN | https://www.seviercountytn.org/gis/ | Shapefile / KML |

> ⚑ **NOTE:** Each county GIS portal must be manually verified at build time.
> Some portals require free account registration for bulk shapefile download.
> Confirm current download URLs and formats before implementation.

### 5.2 Monthly Sync Process

Celery beat runs a monthly parcel sync job:

1. Fires on the 1st of each month at 2:00 AM local time
2. For each enabled county: download latest shapefile or GeoJSON
3. Convert shapefile to GeoJSON using `pyogrio` or `geopandas` if needed
4. Store in PostGIS database with county index
5. Package per-county GeoJSON bundles for PWA download (compressed, ~10–30MB)
6. PWA detects new version hash on next WiFi connection → prompts user to sync
7. User confirms → IndexedDB updated with fresh parcel data

### 5.3 Parcel Lookup Logic

```sql
-- PostGIS: find parcel containing the given point
SELECT parcel_id, owner, address, geom
FROM parcels_{county}
WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326))
LIMIT 1;

-- Return GeoJSON of parcel boundary
SELECT ST_AsGeoJSON(geom) FROM parcels_{county}
WHERE parcel_id = {parcel_id};
```

---

## 6. Waypoint Mission Generation

### 6.1 Flight Parameters

| Parameter | Value |
|-----------|-------|
| Drone | DJI Mini 4 Pro |
| Mission Type | Grid / Lawnmower pattern (nadir, camera straight down) |
| Default Altitude | 120 ft AGL (adjustable 80–200 ft) |
| Forward Overlap | 80% (adjustable) |
| Side Overlap | 75% (adjustable) |
| Camera Angle | 90° nadir (straight down) |
| Speed | Auto-calculated by DJI Fly based on altitude + overlap |
| Output Format | KMZ (DJI Wayline format, compatible with DJI Fly) |

### 6.2 KMZ File Structure

```
mission.kmz
└── wpmz/
    ├── waylines.wpml     ← flight path, altitude, overlap settings
    └── template.kml      ← area boundary polygon
```

```xml
<!-- waylines.wpml core fields -->
<missionConfig>
  <flyToWaylineMode>safely</flyToWaylineMode>
  <finishAction>goHome</finishAction>
  <exitOnRCLost>goContinue</exitOnRCLost>
  <droneInfo><droneEnumValue>67</droneEnumValue></droneInfo>  <!-- Mini 4 Pro -->
</missionConfig>
```

### 6.3 Mission Generation Logic

1. Receive parcel boundary GeoJSON polygon
2. Calculate bounding box + add 15ft buffer around all edges
3. Compute grid flight lines at selected altitude and overlap settings
4. Generate waypoints along each flight line with photo trigger intervals
5. Build `waylines.wpml` and `template.kml` XML files
6. Zip into `.kmz` archive and return to PWA for download

> ⚑ **NOTE:** Use the Waypoint OS API (Pilotbyte) for mission file generation
> where the API supports programmatic KMZ creation. If direct API calls are not
> available, implement the KMZ builder natively in Python using the DJI WPML 2.0
> specification. **(This scaffold implements the native builder.)**

---

## 7. WebODM Integration

### 7.1 Setup

Self-hosted Docker instance exposing a REST API.

| Setting | Value |
|---------|-------|
| Deployment | Docker Compose (local Mac or VPS) |
| Default Port | 8000 |
| API Base URL | `http://localhost:8000/api/` |
| Auth | JWT token from WebODM `/api/token-auth/` |
| Processing Options | `dsm: true, dtm: true, orthophoto-resolution: 2` |

### 7.2 Processing Pipeline

```
# 1. Authenticate
POST /api/token-auth/  { "username": "admin", "password": "..." } → { "token": "abc123" }
# 2. Create project
POST /api/projects/  { "name": "GAS_2024_ProjectName" } → { "id": 42 }
# 3. Upload images + start task
POST /api/projects/42/tasks/  (multipart images[] + options JSON) → { "id": "task-uuid" }
# 4. Poll status
GET /api/projects/42/tasks/task-uuid/  → { "status": 40 }   // 40 = COMPLETED
# 5. Download outputs
GET /api/projects/42/tasks/task-uuid/download/orthophoto.tif
GET /api/projects/42/tasks/task-uuid/download/dsm.tif
GET /api/projects/42/tasks/task-uuid/download/dtm.tif
```

### 7.3 Output Files

| File | Meaning |
|------|---------|
| `orthophoto.tif` | GeoTIFF orthomosaic — flat map + AI feature detection |
| `dsm.tif` | Digital Surface Model — elevation incl. trees/structures |
| `dtm.tif` | Digital Terrain Model — bare earth, used for contours |
| georef | EPSG:4326 (WGS84) — compatible with county GIS parcel data |

---

## 8. AI Feature Detection

### 8.2 Target Feature Classes

| Feature | Detection Method | Planning Relevance |
|---------|------------------|--------------------|
| Water bodies / ponds | Spectral (blue/reflective pixel clustering) | Irrigation source, drainage |
| Tree clusters | NDVI-proxy (green density) + canopy shadow | Obstacle avoidance, root zone |
| Structures / buildings | YOLOv8 object detection | Setback compliance, utility entry |
| Driveways / hardscape | Edge detection + gray tone clustering | Access routes, drainage |
| Fence lines | Edge detection + linear feature extraction | Property boundary confirmation |
| Slope direction | DTM gradient analysis | Water flow routing for irrigation |

### 8.3 Implementation

| Setting | Value |
|---------|-------|
| Model | YOLOv8n (nano) — lightweight, runs on Mac CPU/GPU |
| Pre-trained Dataset | Roboflow Universe — aerial property detection |
| Library | `ultralytics` |
| Input | Orthomosaic GeoTIFF tiled into 640×640 px chips |
| Output | GeoJSON FeatureCollection + confidence scores |
| Minimum Confidence | 0.45 (configurable) |
| Water Detection | `rasterio` + `numpy` spectral clustering (HSV blue range) |
| Slope Analysis | `rasterio` gradient on DTM → aspect + slope rasters |

```python
from ultralytics import YOLO
import rasterio, numpy as np, geopandas as gpd

chips = tile_geotiff("orthophoto.tif", size=640, overlap=64)
model = YOLO("yolov8n-aerial-property.pt")
detections = [model(chip) for chip in chips]
features = merge_detections_to_geojson(detections, ortho_transform)
water_polygons = detect_water_spectral("orthophoto.tif")
features["features"].extend(water_polygons)
slope, aspect = compute_slope_aspect("dtm.tif")
slope_vectors = slope_to_arrows(slope, aspect, spacing=50)
```

---

## 9. Map Output & Print Scaling

### 9.1 Map 1 — Flat Planning Map

Grayscale orthomosaic, high-contrast overlays for hand annotation: bold parcel
boundary (3pt), labeled feature icons, measured grid (e.g. 10 ft squares),
scale bar + ratio, north arrow, title block. PDF (vector) + PNG fallback,
8.5" × 11" single sheet.

### 9.2 Map 2 — Elevation Change Map

Grayscale hillshade from DSM; 1 ft minor / 5 ft major contours; flow-direction
slope arrows at 50 ft spacing; same feature labels; spot elevations; grayscale
only (printer-safe). Accuracy ±1 ft (GCP-free drone GPS).

### 9.3 Scale Calculation

Printable area 7.5" × 10" (8.5×11 with 0.5" margins):

```python
printable_width_inches  = 7.5
printable_height_inches = 10.0
parcel_width_ft  = calculate_width(parcel_geojson)    # e.g., 300 ft
parcel_height_ft = calculate_height(parcel_geojson)   # e.g., 400 ft
scale_w = parcel_width_ft  / printable_width_inches    # 300/7.5 = 40
scale_h = parcel_height_ft / printable_height_inches   # 400/10  = 40
scale = ceil(max(scale_w, scale_h) / 5) * 5            # → 1" = 40 ft
# "Scale: 1 inch = 40 feet | Enlarge 3.33x for 25x30 grid"
enlargement_factor = 25 / 8.5   # = 2.94x  (or 30/11 = 2.73x for height)
```

### 9.4 Map Generation Library

Primary: PyQGIS (full cartographic control). Alternative: Matplotlib + rasterio
+ geopandas (lighter, no QGIS dependency). Export ≥300 DPI PDF; Arial/Helvetica
labels.

---

## 10. Offline Architecture

**Works offline:** address entry + cached geocoding, parcel lookup (IndexedDB
GeoJSON), MapLibre offline tiles, client-side KMZ generation, KMZ download,
queued project creation.

**Requires connectivity:** image upload to WebODM, WebODM processing, map PDF
generation, monthly parcel sync, initial authentication.

**Service worker strategy:** app shell cache-first; API network-first with
offline fallback queue; parcel GeoJSON in IndexedDB (not SW cache); MapLibre
offline tile pack per county; Background Sync API fires on WiFi.

---

## 11. Data Model

### 11.1 Project Schema

```
Project {
  id:            UUID
  created_at:    DateTime
  address:       String
  county:        Enum(blount, knox, sevier)
  lat:           Float
  lng:           Float
  parcel_id:     String
  parcel_geojson: GeoJSON Polygon
  status:        Enum(setup, mission_ready, flying, processing, complete)
  mission_kmz:   File path
  ortho_tif:     File path
  dsm_tif:       File path
  dtm_tif:       File path
  features_geojson: GeoJSON FeatureCollection
  map_flat_pdf:  File path
  map_elev_pdf:  File path
  print_scale:   String (e.g., "1 inch = 40 feet")
  notes:         String
  use_case:      Enum(irrigation, hardscape, both)
}
```

### 11.2 Feature GeoJSON Schema

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [] },
      "properties": {
        "feature_type": "pond",
        "label": "Pond",
        "confidence": 0.87,
        "area_sqft": 1240.5,
        "notes": ""
      }
    }
  ]
}
```

---

## 12. Development Phases & Priorities

- **Phase 1 — MVP (immediate):** PWA scaffold (address → geocode → parcel →
  map), county GIS (Blount first), KMZ generator, offline cache + monthly sync,
  DJI Fly share-sheet handoff.
- **Phase 2 — Processing pipeline:** WebODM Docker + API, image upload, ortho +
  DEM retrieval, basic flat map.
- **Phase 3 — Elevation & features:** contours from DTM, slope arrows, AI
  detection (YOLOv8 + spectral water), feature overlay.
- **Phase 4 — Polish & scale:** Knox + Sevier feeds, annotation layer, project
  history, multi-user login.

---

## 13. Environment & Dependencies

See [`backend/requirements.txt`](../backend/requirements.txt) and
[`pwa/package.json`](../pwa/package.json).

**Infrastructure:** MacBook Pro M-series (WebODM Docker + backend); PostgreSQL 15
+ PostGIS 3; Redis (Celery broker); Tailscale for field remote access; Cloudflare
Tunnel or ngrok for the PWA's HTTPS requirement.

> ⚑ **NOTE:** PWA install on iPhone requires HTTPS. Use Cloudflare Tunnel (free)
> to expose the local backend with a valid SSL cert, or deploy to a VPS with
> Let's Encrypt.

---

## 14. Developer Handoff Notes

### 14.1 Build Order

Start with **Phase 1 MVP only.** Do not build WebODM or AI detection until KMZ
generation and offline parcel lookup are solid. The operator needs to fly within
the first sprint.

### 14.2 Key Constraints

- **iPhone-first:** test every screen on Safari iOS (PWA installs via Safari only).
- **Offline is non-negotiable:** poor LTE at East TN field sites.
- **DJI Mini 4 Pro:** `droneEnumValue` in WPML is **67** — confirm on WPML 2.0 spec.
- **Map output:** 8.5×11 single sheet, ≥300 DPI, PDF.
- **Scale bar + ratio text required** on every map.
- **All elevation data in feet** (not meters).

### 14.3 Questions to Resolve at Kickoff

1. Confirm Waypoint OS API endpoint for programmatic KMZ — or implement native WPML builder.
2. Verify Blount/Knox/Sevier county GIS download URLs and shapefile schemas.
3. Confirm WebODM hosting: Mac Mini server vs VPS.
4. Select YOLOv8 aerial detection model from Roboflow Universe — test on East TN imagery.
5. Confirm HTTPS solution: Cloudflare Tunnel or VPS deployment.

### 14.4 Contact / Project Context

| | |
|---|---|
| Client | Ryan Olive — Guardian Aerial Solutions / TNC |
| Location | Maryville, Tennessee |
| Primary Drone | DJI Mini 4 Pro |
| Use Cases | Irrigation planning, hardscape/landscape construction |
| Counties | Blount, Knox, Sevier (East Tennessee) |
| Dev Environment | MacBook Pro M-series Max |
| Spec Version | 1.0 — June 2026 |
