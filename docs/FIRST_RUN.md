# First run — start the backend on your Mac and log in

A start-to-finish guide to run the **real** system (not just the UI preview) on
your MacBook Pro and sign in from your iPhone.

Time: ~15 minutes the first time (most of it Docker pulling images).

---

## 0. Install the prerequisites (one time)

- **Docker Desktop** — <https://www.docker.com/products/docker-desktop/>
- **Node.js 20+** — <https://nodejs.org/> (or `brew install node`)
- The repo cloned locally:
  ```bash
  git clone https://github.com/OliveR19333/Lens-ai.git
  cd Lens-ai
  ```

---

## 1. Configure backend secrets

```bash
cd backend
cp .env.example .env
```

Open `.env` and set at least these:

```ini
ADMIN_USERNAME=admin
ADMIN_PASSWORD=pick-a-real-password      # <- this is your login
JWT_SECRET=paste-a-long-random-string    # python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

> **Your login = `ADMIN_USERNAME` / `ADMIN_PASSWORD`.** Change them here.

---

## 2. Start everything with Docker

From the repo root:

```bash
cd infra
docker compose up -d        # Postgres/PostGIS, Redis, backend API, Celery worker + beat
```

Wait until `docker compose ps` shows the services healthy. The API is now at
**http://localhost:8080** (try **http://localhost:8080/health** → `{"status":"ok"}`,
and **http://localhost:8080/docs** for the full API).

### Create the database tables (first time only)

```bash
docker compose exec backend python -m app.cli initdb
```

You should see `✅ Database initialized`.

---

## 3. Load some parcel data (so the field flow works)

Automated county sync needs a verified GIS URL (see
[`GIS_DATA_SOURCES.md`](GIS_DATA_SOURCES.md)). The quickest path right now:

1. Download a county parcels **GeoJSON** from the TN open-data portal
   <https://tn-tnmap.opendata.arcgis.com/> (filter to Blount/Knox/Sevier).
2. In the PWA: **Settings → Import parcel data** → pick the county → choose the
   file. It's stored on the device for fully offline lookup.

---

## 4. Run the PWA pointed at your backend

In a second terminal, from the repo root:

```bash
cd pwa
cp .env.example .env
# edit .env → VITE_API_BASE_URL=http://localhost:8080
npm install
npm run dev          # http://localhost:5173
```

Open **http://localhost:5173** in your browser and log in with the
`ADMIN_USERNAME` / `ADMIN_PASSWORD` you set in step 1. 🎉

---

## 5. Use it on your iPhone (needs HTTPS)

iOS only installs a PWA over **HTTPS**. Two easy options:

- **Same WiFi, quick test:** run `npm run dev -- --host` and open the
  `http://<your-mac-ip>:5173` URL on the phone (works for trying it; iOS won't
  let you *install* it without HTTPS).
- **Proper HTTPS (recommended):** expose the backend with a free **Cloudflare
  Tunnel** (`cloudflared tunnel --url http://localhost:8080`), set the PWA's
  `VITE_API_BASE_URL` to that HTTPS URL, rebuild (`npm run build`), and serve it
  (or use the same tunnel trick for the PWA). Then on the iPhone: open the HTTPS
  URL in **Safari → Share → Add to Home Screen**.

See [`OFFLINE_AND_HOSTING.md`](OFFLINE_AND_HOSTING.md) for the full hosting
picture (and why the field flow works with the Mac off).

---

## 6. Add your team (e.g. Devan)

Either in the app — **Settings → Add Team Member** — or from the CLI:

```bash
docker compose exec backend python -m app.cli createuser devan a-temp-password "Devan Teaster"
```

---

## Troubleshooting

| Symptom | Fix |
|--------|-----|
| Login fails with "server unreachable" | Backend not running / wrong `VITE_API_BASE_URL`. Check `http://localhost:8080/health`. |
| Login fails with "invalid username" | Credentials don't match `.env`. Restart backend after editing `.env`. |
| "No parcel found" in the field flow | Import the county parcels first (step 3). |
| iPhone won't "Add to Home Screen" | You must be on **HTTPS** (step 5) and using **Safari**. |
| Photo upload / map render fails | Those need WiFi + the backend (and WebODM for processing). The mission/KMZ flow works offline. |

---

## What needs real external setup later

- **WebODM** (photo → orthomosaic): run its own Docker app and set
  `WEBODM_BASE_URL` + credentials in `.env`.
- **AI detection model**: drop a trained YOLOv8 aerial model at `YOLO_MODEL_PATH`
  (water + slope detection run without it).
- **Automated county sync**: confirm the GIS layer URL (one-time, see
  `GIS_DATA_SOURCES.md`).
