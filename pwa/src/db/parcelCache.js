// Offline parcel + geocode cache in IndexedDB (spec §3.2, §10.1, §10.3).
// Per-county parcel GeoJSON bundles can be ~50MB, so they live here rather than
// in the service-worker cache.
import { openDB } from 'idb'

const DB_NAME = 'gas-parcels'
const DB_VERSION = 1

const STORE_PARCELS = 'parcels' // key: county -> { version_hash, geojson, syncedAt }
const STORE_GEOCODE = 'geocode' // key: normalized address -> result
const STORE_QUEUE = 'queue' // offline write queue (project creation, etc.)

async function db() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(d) {
      if (!d.objectStoreNames.contains(STORE_PARCELS)) d.createObjectStore(STORE_PARCELS)
      if (!d.objectStoreNames.contains(STORE_GEOCODE)) d.createObjectStore(STORE_GEOCODE)
      if (!d.objectStoreNames.contains(STORE_QUEUE))
        d.createObjectStore(STORE_QUEUE, { keyPath: 'id', autoIncrement: true })
    }
  })
}

// ---- County parcel bundles ----
export async function saveCountyBundle(county, versionHash, geojson) {
  const d = await db()
  await d.put(STORE_PARCELS, { versionHash, geojson, syncedAt: Date.now() }, county)
}

export async function getCountyBundle(county) {
  const d = await db()
  return d.get(STORE_PARCELS, county)
}

export async function getCachedCounties() {
  const d = await db()
  const keys = await d.getAllKeys(STORE_PARCELS)
  const out = []
  for (const k of keys) {
    const v = await d.get(STORE_PARCELS, k)
    out.push({ county: k, versionHash: v?.versionHash, syncedAt: v?.syncedAt })
  }
  return out
}

// ---- Geocode cache (recently searched addresses, spec §3.2) ----
export async function cacheGeocode(address, result) {
  const d = await db()
  await d.put(STORE_GEOCODE, result, address.trim().toLowerCase())
}

export async function getCachedGeocode(address) {
  const d = await db()
  return d.get(STORE_GEOCODE, address.trim().toLowerCase())
}

// ---- Offline write queue (spec §10.1 — project creation queued offline) ----
export async function enqueue(item) {
  const d = await db()
  await d.add(STORE_QUEUE, { ...item, queuedAt: Date.now() })
  return queueDepth()
}

export async function queueDepth() {
  const d = await db()
  return d.count(STORE_QUEUE)
}

export async function drainQueue(handler) {
  const d = await db()
  const all = await d.getAll(STORE_QUEUE)
  for (const item of all) {
    try {
      await handler(item)
      await d.delete(STORE_QUEUE, item.id)
    } catch {
      // leave in queue; retry on next sync
    }
  }
  return queueDepth()
}
