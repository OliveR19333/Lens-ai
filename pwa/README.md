# GAS Property Mapping — PWA (React + Vite)

Mobile-first, offline-capable Progressive Web App for the GAS Property Mapping
System (spec §3). Install to the iPhone home screen via Safari; all mission
setup works offline (spec §10.1).

## Stack (spec §3.1)

React 18 · Vite · vite-plugin-pwa (Workbox) · MapLibre GL JS · Zustand · Axios ·
IndexedDB (`idb`) · Tailwind CSS · Lucide icons.

## Run

```bash
npm install
cp .env.example .env       # set VITE_API_BASE_URL
npm run dev                # http://localhost:5173
npm run build && npm run preview
```

> The service worker is only active in the production build (`devOptions.enabled`
> is `false`). Test offline behavior with `npm run build && npm run preview`.

## Screen flow (spec §3.3)

`Login → Dashboard → New Mission → Parcel Preview → Mission Output → Upload
Images → Map Viewer → Print/Export`, plus `Settings`. Routing lives in
`src/App.jsx`; a route guard redirects to `/login` without a JWT.

## Source map

```
src/
├── main.jsx              bootstrap + connectivity/queue wiring
├── App.jsx               routes + auth guard
├── store/useStore.js     Zustand global state (auth, draft, counties)
├── api/client.js         Axios client + endpoint wrappers + offline geocode
├── db/parcelCache.js     IndexedDB: parcel bundles, geocode cache, write queue
├── lib/dji.js            DJI Fly share-sheet handoff (spec §3.4)
├── components/           Layout, ui primitives, ParcelMap (MapLibre)
└── screens/              the 9 screens of §3.3
```

## Offline behavior (spec §10)

- **App shell**: precached (cache-first) by Workbox.
- **Geocoding**: network-first with an IndexedDB fallback for recently searched
  addresses.
- **Parcel GeoJSON**: stored in IndexedDB (not the SW cache — bundles are large).
- **Basemap tiles**: cache-first MapLibre tile cache.
- **Write queue**: project creation is queued offline and drained on reconnect.

## iPhone notes (spec §14.2)

PWA install requires **HTTPS** and **Safari** on iOS. Expose the backend over
HTTPS with a Cloudflare Tunnel (free) or a VPS + Let's Encrypt (spec §13.3).
Drop real launcher icons into `public/icons/` before a production build.
