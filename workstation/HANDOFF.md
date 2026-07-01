# TNC-GAS Property Mapping — Handoff Summary

_Last updated: 2026-07-01_

## TL;DR
A **local, offline drone-mapping workstation** on the Mac (M5 Max, 48 GB). Turns a
property **address + a short drone flight** into a **scaled, measurable map** with
the county parcel boundary on top. **Proven end-to-end and accurate to the inch**
on 210 Mike White Ln, Friendsville (Blount Co.). Free tools, no cloud, no monthly bills.

---

## What works right now ✅
- **Address lookup** — `find("address")` in QGIS jumps to the parcel (all 4 counties loaded).
- **Fly → geotag → process → map** — video + `.SRT` → geotagged frames → WebODM → orthophoto + elevation. Georeferenced, measures to the inch.
- **Measure** — distances (ft) + areas (sq ft) that stay on the map and print.
- **One-click "Make Map"** — Desktop app: pick a flight folder → it does everything.
- **Print sheets** — `site-plan.pdf` + `topo.pdf` (first drafts; see "in progress").
- Everything **committed to GitHub** (PR #1) and documented in `HANDBOOK.md`.

## In progress / not finished ⏳
- **Print sheets** need dialing in (grid density, background opacity, layout, contour spacing). Tunable via `make_prints(folder, grid_div, bg_opacity)`.
- **SAM AI feature-tracing (Geo-SAM)** — plugin + PyTorch **installed**, but not yet used. Next: point it at a clean ortho and click features (house, driveway) to auto-outline them.
- **Google Drive auto-backup** — deferred (connector approval was flaky).
- **Retire the `tnc-gas` cloud server** — kept for later reuse (address lookup / client sharing).

---

## Daily workflow (per property)
1. QGIS: open `~/TNC-GAS/templates/TNC-base.qgz` → `find("address")` → confirm the lot.
2. Fly it — camera straight down, **Video Subtitles ON** (for the `.SRT` GPS). Best: **4K, 30fps, Normal color** (not D-Log).
3. Drop the `.MP4` + `.SRT` into a new `~/TNC-GAS/jobs/2026/<address>/` folder.
4. **Double-click "Make Map"** on the Desktop → pick that folder → it geotags, processes, and opens the map.
5. In QGIS: drag in the `orthophoto.tif`, measure, and (later) trace / print.

## Where everything lives
```
~/TNC-GAS/
  county-data/   Blount, Loudon, Monroe, Sevier parcels (+ streets, water)
  jobs/2026/     one folder per property (video, .SRT, frames/, map/)
  tools/         the scripts (below)
  templates/     TNC-base.qgz  <- open this
  outputs/       finished deliverables
~/Desktop/Make Map.command     <- one-click pipeline
```
Repo: GitHub `OliveR19333/Lens-ai`, branch `claude/new-session-hzjb8c`, PR #1.
The `workstation/` folder in the repo holds copies of all tools + `HANDBOOK.md`.

## The tools (in `~/TNC-GAS/tools/`, run in QGIS Python Console unless noted)
| Tool | What it does |
|------|--------------|
| `tnc_video.py` | (Terminal) video + `.SRT` → geotagged frames |
| `tnc_process.py` | (Terminal) frames → WebODM → orthophoto + DSM/DTM |
| `Make Map.command` | (Desktop, double-click) runs the whole pipeline |
| `build_project.py` | rebuilds `TNC-base.qgz` (counties + satellite + labels) |
| `find_address.py` | `find("address")` → zoom + pin the property |
| `measure.py` | `measure_line()` / `measure_area()` → printable dimensions |
| `make_prints.py` | `make_prints(folder, grid_div, bg_opacity)` → site-plan + topo PDFs |
| `nudge.py` | shift the ortho onto the parcel (⚠️ edits the file — see gotchas) |

---

## Gotchas / lessons learned
- **WebODM must be running** to process (Docker Desktop up → WebODM Manager or `webodm.sh start`). "Connection refused" = it's not running.
- **Docker memory** must be ~32 GB (Docker → Settings → Resources) or processing fails "Not enough memory".
- **Parcel labels are scale-dependent** — they only show when zoomed IN to a property (by design).
- **Layer order** matters: Parcels (top, see-through) → orthophoto → satellite (bottom).
- **~7 ft absolute offset is normal** — consumer drone GPS isn't RTK. It does NOT affect measurements (those are inch-accurate). Left as-is.
- **`nudge.py` edits the ortho file in place** and scrambled one map during testing — prefer to just accept the offset, or rebuild from `frames/` if a map gets corrupted (`tnc_process.py <folder>/frames`).
- QGIS opens a **blank project on restart** — reopen `TNC-base.qgz`. Nothing is ever lost; the data is all in files.

## "Get back to solid ground" recipe
1. QGIS → Project → Open → `~/TNC-GAS/templates/TNC-base.qgz`
2. Need a map? Double-click **Make Map** → pick flight folder
3. Drag the fresh `orthophoto.tif` in

---

## History (why it's built this way)
Started as a hosted PWA + **automated DJI waypoint missions**. Automated flight hit a
hard wall — the sealed **DJI RC 2 won't accept imported missions** on current firmware
(tried adb, MTP, SD card, factory reset — all blocked). Pivoted to **manual flight +
local processing (WebODM + QGIS)**, which turned out simpler, free, and accurate to the
inch. The parcel `.SRT` GPS (from video subtitles) is what georeferences the map.

## Next session — pick up here
1. **Clean ortho** for Mike White (nudge scrambled it): `python3 ~/TNC-GAS/tools/tnc_process.py ~/TNC-GAS/jobs/2026/mike-white-210/frames`
2. **Geo-SAM tracing**: point it at the clean ortho, click house/driveway/beds → outlines.
3. **Finish the print sheets** (grid/opacity/layout).
4. Optional: Google Drive auto-backup; retire the cloud server.
