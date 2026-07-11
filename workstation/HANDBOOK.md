# TNC-GAS Property Mapping — Operator's Handbook

A local, offline drone-mapping workstation. Turn a property address + a short
drone flight into a **scaled, measurable map** (accurate to the inch) with the
county parcel boundary on top — all on the Mac, no cloud, no monthly bills.

Proven end-to-end on 210 Mike White Ln, Friendsville (Blount Co.): address →
parcel → 1-minute flight → georeferenced map that measured to the inch.

---

## What's installed (one-time, already done)

| Piece | What it does |
|-------|--------------|
| **Docker Desktop** | Runs the map engine |
| **WebODM** (via WebODM Manager) | Turns drone frames into the map — `http://localhost:8000` |
| **QGIS** | View, measure, mark up, print; holds the county parcel data |
| **ffmpeg + exiftool** | Pull frames from video + stamp GPS onto them |
| `~/TNC-GAS/` | The reference folder where everything lives |

Reference folder layout:
```
~/TNC-GAS/
  county-data/   Blount, Loudon, Monroe, Sevier parcel shapefiles
  jobs/2026/     one folder per property (video, .SRT, frames, map)
  tools/         tnc_video.py, tnc_process.py, find_address.py, build_project.py
  templates/     TNC-base.qgz  (open this — all counties + satellite)
  outputs/       finished maps / client PDFs
```

---

## The per-property recipe

### 1. Research the property (QGIS)
- Open `~/TNC-GAS/templates/TNC-base.qgz`.
- In the **Python Console** (Plugins → Python Console), once per session:
  ```python
  exec(open('/Users/ryanolive/TNC-GAS/tools/find_address.py').read())
  ```
- Jump to any property:
  ```python
  find("210 Mike White Ln, Friendsville, TN 37737")
  ```
  Red pin drops on the block; confirm the exact lot with the **Identify** (ℹ️) tool.

### 2. Fly it
- Camera **straight down (−90°)**, **Video Subtitles ON** (this makes the `.SRT` GPS).
- Best settings: **4K, 30fps, Normal color** (not D-Log), fast shutter, bright day.
- Fly smooth, slow, overlapping passes (lawnmower pattern), a few seconds past each edge.

### 3. Copy the flight to a job folder
Put the **`.MP4` and `.SRT`** into a new folder, e.g.:
```
~/TNC-GAS/jobs/2026/<address>/
```

### 4. Geotag the frames
```bash
python3 ~/TNC-GAS/tools/tnc_video.py ~/TNC-GAS/jobs/2026/<address>
```
(Add ` 2` on the end for 2 fps / more overlap if a map comes out with gaps.)

### 5. Build the map
Make sure **Docker + WebODM are running** (see below), then:
```bash
python3 ~/TNC-GAS/tools/tnc_process.py ~/TNC-GAS/jobs/2026/<address>/frames
```
Enter the WebODM login (`TNC.GAS`). The map saves to `~/Desktop/TNC_map_...`
(`orthophoto.tif` = the map, `dsm.tif`/`dtm.tif` = elevation).

### 6. Measure + finish (QGIS)
- Drag `orthophoto.tif` into QGIS; drag the parcel layer **above** it so lines show on top.
- Right-click the ortho → **Zoom to Layer**.
- **Measure tool** (ruler): Measure Line for distances, Measure Area for square footage
  — set units to **Feet / Square Feet**.

---

## Starting WebODM (if processing says "Connection refused")

1. Open **Docker Desktop**; wait for the whale 🐳 in the menu bar to go steady.
2. Start WebODM (either):
   - Open the **WebODM Manager** app, or
   - ```bash
     cd "$HOME/Library/Application Support/com.masseranolabs.WebODM-Manager/WebODM" && ./webodm.sh start
     ```
3. Confirm `http://localhost:8000` loads.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Connection refused` on processing | WebODM not running — start Docker + WebODM (above) |
| Processing fails "Not enough memory" | Docker Desktop → Settings → Resources → Memory ≈ 32 GB → Apply & Restart |
| Map lands in the ocean | Frames weren't geotagged — re-run step 4 (need the `.SRT`) |
| Map has holes/gaps | Re-run step 4 at 2 fps: `tnc_video.py <folder> 2` |
| Address "not found" | Rural road — use GPS in the locator bar, or click the parcel by eye |
| Parcels cover the drone map | In Layers panel, drag parcel layers above the orthophoto |

---

## Optional future upgrades
- **One-command automation** — fold steps 4–6 into a single `make-map <folder>`.
- **Print/PDF layout template** for client bids.
- **Google Drive backup** of each job.
- **AI auto-detect** turf/hardscape/beds from the ortho for automatic areas.

The cloud app + `tnc-gas` server are retired-in-place; repurpose later for
address lookup / client sharing if wanted.
