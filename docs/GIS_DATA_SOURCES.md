# County parcel data sources (spec §5.1)

Findings from researching the parcel GIS endpoints for Blount, Knox, and Sevier
counties, and the recommended way to wire automated sync.

> **Status:** the build sandbox could not reach these government GIS hosts to
> confirm exact layer paths (outbound requests to `*.arcgis.com`, `kgis.org`,
> and `tnmap.tn.gov` were blocked, and WebFetch returned 403). The research
> below identifies the right source and the precise fields to fill in;
> **final confirmation is a one-time manual step** — open each REST directory in
> a browser, copy the parcels layer `/query` URL, and set `service_url` +
> `where_clause` in `backend/app/gis/county_sync.py`, then flip `verified=True`.

## Recommended: Tennessee statewide Comptroller parcel layer

Use **one** authoritative statewide layer, filtered by county, instead of three
separate county servers.

- **Why:** covers all 95 counties, updates **monthly around the 1st business
  day** (matches our Celery sync cadence, spec §5.2), and is explicitly
  published for public/government **download** — so it sidesteps the bulk-
  retrieval restrictions some county servers impose.
- **Open-data portal (download by county):** <https://tn-tnmap.opendata.arcgis.com/>
- **REST root:** <https://tnmap.tn.gov/arcgis/rest/services/>
- **Comptroller parcel data page:**
  <https://comptroller.tn.gov/office-functions/pa/gisredistricting/redistricting-and-land-use-maps/parcel-data.html>

To wire it: find the statewide parcels `FeatureServer`/`MapServer` layer under
the REST root, set every county's `service_url` to that layer's base, and keep
the per-county `where_clause` (e.g. `UPPER(CONAME)='BLOUNT'`). Confirm the actual
county field name (`CONAME` is the typical Comptroller field) and the
parcel-id/owner/address field names, then extend `gis/normalize.py` aliases if
needed.

## Per-county notes

| County | Portal / REST | Notes |
|--------|---------------|-------|
| **Blount** | County server: `https://com.blountgis.org/server/rest/services` and `https://web5.kcsgis.com/kcsgis/rest/services/Blount/Public/MapServer` | ⚠️ **The county/KCS server prohibits automated bulk retrieval.** Use the TN statewide layer instead. Open-data: <https://tn-tnmap.opendata.arcgis.com/> |
| **Knox (KGIS)** | `https://www.kgis.org/gisserver/rest/services/` | KGIS publishes parcels via ArcGIS REST (a `Planning_Casses/MapServer/25` layer exists; locate the dedicated parcels layer). The statewide layer also covers Knox. |
| **Sevier** | <https://tn-tnmap.opendata.arcgis.com/> | No friction-free dedicated county REST confirmed; use the statewide layer filtered to Sevier. |

## How the sync consumes this

`gis/county_sync.py` → `sync_county(key)`:

1. `arcgis.fetch_layer_geojson(service_url, where=where_clause)` — paginated
   GeoJSON pull (already implemented + tested).
2. `normalize.normalize_collection(...)` — map raw fields to
   `parcel_id` / `owner` / `address` / `county`.
3. `bundle.package_bundle(...)` — gzip + version hash for the PWA.
4. Optional PostGIS load for server-side lookup.

Until `service_url` is set, automated sync is skipped with a clear log message
and operators load parcels via the PWA's **Settings → Import parcel data**
(download a county GeoJSON from the open-data portal, import once, works fully
offline thereafter).
