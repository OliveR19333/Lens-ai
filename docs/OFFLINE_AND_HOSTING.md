# Running on your Mac & working offline

How the GAS Property Mapping System is meant to run for a single operator who
hosts on a Mac but works in the field with just an iPhone.

## The short version

- **Field work (locate → measure → generate flight plan → fly): 100% offline.**
  It runs entirely on the iPhone. No Mac, no signal.
- **Post-flight (upload photos → stitch → maps): on WiFi**, talking to the Mac.
- Internet is only required if you want to reach the Mac **while away from it**.

## What runs where

| Step | Where it runs | Needs internet? |
|------|---------------|-----------------|
| Locate property (GPS) | iPhone (device GPS) | ❌ No |
| Locate by street address | Backend geocode (US Census) | ✅ Yes (or a previously cached address) |
| Find parcel boundary | iPhone, against cached county data | ❌ No |
| Measure (size, area, scale) | iPhone | ❌ No |
| Generate DJI mission (KMZ) | iPhone (in-browser) | ❌ No |
| Hand off to DJI Fly | iPhone share sheet | ❌ No |
| Upload photos → WebODM | Mac | ✅ WiFi to the Mac |
| Stitch ortho + elevation | Mac | ✅ |
| Render print maps (PDF) | Mac | ✅ |

The field column is the whole point: **stand on the property, tap “Use my
location”, confirm the parcel, generate the KMZ, fly** — with the phone in
airplane mode if you like.

## One-time setup before you leave WiFi

1. **Install the app** to the iPhone home screen (Safari → Share → Add to Home
   Screen). After the first load it opens offline forever.
2. **Load county parcel data** so offline lookup has something to search:
   - Settings → **Import parcel data** → pick the county → choose the GeoJSON
     file you downloaded from the county GIS portal. Stored on the phone.
   - (Later, the automated monthly sync from the Mac will do this for you — spec
     §5.2. Until that’s wired, manual import is the way.)
3. Optional: search any addresses you already know at home so they’re cached.

That’s it. Now the field flow works with no Mac and no signal.

## Hosting on the Mac

The Mac is the **server** for the post-flight half (WebODM stitching, map
rendering, the database). Run it with Docker:

```bash
cd infra
docker compose up -d      # Postgres/PostGIS + Redis + backend + worker
# WebODM runs from its own compose — see infra/docker-compose.yml note.
```

### Reaching the Mac

- **Same WiFi as the Mac** (e.g. at home/shop): the iPhone reaches it directly
  at the Mac’s local address (e.g. `http://192.168.1.50:8080`). No internet.
- **Away from the Mac, want to reach it:** the Mac must be **awake and online**,
  and you need a tunnel so the phone can find it across the internet —
  **Tailscale** (private, easiest) or **Cloudflare Tunnel** (gives an HTTPS URL).
  Both free (spec §13.3).

> The iPhone PWA install requires **HTTPS**. On the same LAN that means a local
> certificate or a tunnel; Cloudflare Tunnel is the simplest way to get a valid
> HTTPS URL pointing at your Mac.

### If the Mac is off

Nothing post-flight works (no stitching/maps) until it’s back on — those jobs
just queue. **The field flow is unaffected**, because it never needed the Mac.

## Honest limitations

- **Brand-new address with no signal can’t be geocoded.** Street address →
  GPS needs the internet (or a previously cached lookup). In the field, use
  **“Use my location”** instead — the phone’s GPS works offline.
- **Offline parcel lookup only covers counties you’ve loaded** onto the phone.
- **Photo upload needs real bandwidth** (WiFi/LTE) — image sets are too large to
  queue offline (spec §10.2).
