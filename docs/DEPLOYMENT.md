# Production deployment — a real, installable app

How to turn this repo into **an app you install on your iPhone home screen**,
reachable from anywhere, with WebODM and AI detection wired in.

## Is the PWA a "real app"?

Yes — for your use case it behaves like one. Installed to the home screen it has
its own icon, runs full-screen (no browser bars), works offline, and updates
itself. The only thing it is *not* is an App Store listing. A native App Store
app would add a $99/yr Apple Developer account, app review, and a rewrite/wrapper
— not worth it to start. **Recommended path: PWA on a domain with HTTPS.**

---

## Architecture

```
            ┌─────────────── your VPS (or Mac) ───────────────┐
  iPhone ── HTTPS ──▶  Caddy  ──/──▶  PWA static files
                        │      ──/api─▶  FastAPI backend ──▶ Postgres/PostGIS
                        │                      │            └─▶ Redis ◀─ Celery
                        │                      └─▶ WebODM (host) ─▶ ortho/DEM
                        └─ auto Let's Encrypt cert (HTTPS)
```

One domain. Caddy serves the app and proxies `/api/*` to the backend, and gets a
TLS certificate automatically — which is what lets iOS install the PWA.

---

## A. One-time things you provide

1. **A server.** A small **VPS** (DigitalOcean/Linode, ~$12–40/mo depending on
   whether WebODM runs there too) is recommended so the app is always reachable
   even when your Mac is off. Your Mac works too for testing.
2. **A domain** (e.g. `mapping.guardianaerial.com`) with a DNS **A record**
   pointing at the server's IP. ~$12/yr.
3. **Secrets** in `backend/.env`: `ADMIN_PASSWORD`, a strong `JWT_SECRET`,
   `POSTGRES_PASSWORD`.

---

## B. Deploy the stack

On the server, with Docker installed:

```bash
git clone https://github.com/OliveR19333/Lens-ai.git && cd Lens-ai
cp backend/.env.example backend/.env      # then edit secrets

cd infra
DOMAIN=mapping.example.com docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python -m app.cli initdb
```

Open `https://mapping.example.com` → log in with `ADMIN_USERNAME` /
`ADMIN_PASSWORD`. On the iPhone: **Safari → Share → Add to Home Screen**. 🎉

---

## C. WebODM (drone photos → orthomosaic + elevation)

WebODM runs as its own stack. On the server (or your Mac):

```bash
./infra/setup-webodm.sh        # clones + starts WebODM on :8000
```

Create its admin account in the browser, then put in `backend/.env`:

```ini
WEBODM_BASE_URL=http://host.docker.internal:8000/api
WEBODM_USERNAME=...
WEBODM_PASSWORD=...
```

Restart the backend + worker. Now uploading photos produces the real
ortho/DEM that feed both maps.

> WebODM processing is RAM/CPU heavy. If it runs on the same VPS, size it
> accordingly (8 GB+); many operators run WebODM on the Mac and the app on a
> small VPS.

---

## D. AI feature detection model

Pick a trained model from **Roboflow Universe** (search "aerial property",
"building footprint aerial", "swimming pool aerial"), export as **YOLOv8 PyTorch
(.pt)**, and drop it in:

```bash
python backend/scripts/fetch_model.py "<roboflow .pt url>" infra/models/yolov8n-aerial-property.pt
```

It's mounted into the backend at `/app/models` and picked up via
`YOLO_MODEL_PATH`. Without a model, **water + slope detection still run**; the
model adds structures/driveways/etc. Test it on a few East TN orthomosaics and
tune `FEATURE_MIN_CONFIDENCE`.

---

## E. Updating

```bash
git pull
docker compose -f infra/docker-compose.prod.yml up -d --build
```

The PWA's service worker auto-updates clients on next launch.

---

## Quick checklist

- [ ] VPS provisioned, Docker installed
- [ ] Domain A record → server IP
- [ ] `backend/.env` secrets set
- [ ] `docker compose -f infra/docker-compose.prod.yml up -d --build`
- [ ] `app.cli initdb`
- [ ] Parcel data imported (Settings → Import) or auto-sync URL confirmed
- [ ] WebODM running + creds in `.env`
- [ ] YOLO model in `infra/models/`
- [ ] Installed to iPhone home screen over HTTPS
