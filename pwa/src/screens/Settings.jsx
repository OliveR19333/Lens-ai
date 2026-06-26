import { useEffect, useState } from 'react'
import { RefreshCw, Upload } from 'lucide-react'
import { useStore } from '../store/useStore'
import { listCounties, syncParcels, parcelManifest, downloadCountyBundle } from '../api/client'
import { getCachedCounties, getCountyBundle, saveCountyBundle } from '../db/parcelCache'
import { Button, Card, Banner } from '../components/ui'

const COUNTIES = [
  { county: 'blount', county_name: 'Blount County' },
  { county: 'knox', county_name: 'Knox County' },
  { county: 'sevier', county_name: 'Sevier County' }
]

// Cheap content hash so the PWA can tell when a bundle changed (spec §5.2).
function quickHash(str) {
  let h = 5381
  for (let i = 0; i < str.length; i++) h = ((h << 5) + h + str.charCodeAt(i)) >>> 0
  return h.toString(16)
}

// Settings (spec §3.3) — county selection, sync, account, and a manual
// parcel-data import so the offline field flow works before the automated
// monthly GIS sync is wired (spec §5.2 is a backend stub).
export default function Settings() {
  const username = useStore((s) => s.username)
  const online = useStore((s) => s.online)
  const counties = useStore((s) => s.counties)
  const setCounties = useStore((s) => s.setCounties)
  const [cached, setCached] = useState([])
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)
  const [importCounty, setImportCounty] = useState('blount')

  async function refreshCache() {
    setCached(await getCachedCounties())
  }

  useEffect(() => {
    refreshCache()
    if (online) listCounties().then(setCounties).catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [online])

  // Pull updated county bundles from the server into IndexedDB (spec §5.2).
  // Only downloads counties whose server version differs from what's cached.
  async function onSync() {
    setBusy(true)
    setMsg('')
    try {
      const { counties: manifest } = await parcelManifest()
      const available = manifest.filter((c) => c.available)
      if (available.length === 0) {
        // Nothing packaged yet — kick the server-side refresh job.
        const res = await syncParcels()
        setMsg(res.message || 'No bundles ready yet — asked the server to build them. Try again shortly.')
        return
      }
      let updated = 0
      for (const c of available) {
        const local = await getCountyBundle(c.county)
        if (local?.versionHash === c.version_hash) continue
        const { geojson, version } = await downloadCountyBundle(c.county)
        await saveCountyBundle(c.county, version || c.version_hash, geojson)
        updated++
      }
      await refreshCache()
      setMsg(updated ? `Downloaded ${updated} county bundle(s) — available offline.` : 'Already up to date.')
    } catch {
      setMsg('Could not reach the server — use manual import below to work offline now.')
    } finally {
      setBusy(false)
    }
  }

  async function onImport(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setMsg('')
    try {
      const text = await file.text()
      const geojson = JSON.parse(text)
      if (geojson.type !== 'FeatureCollection' || !Array.isArray(geojson.features)) {
        throw new Error('Not a GeoJSON FeatureCollection.')
      }
      await saveCountyBundle(importCounty, quickHash(text), geojson)
      await refreshCache()
      setMsg(`Imported ${geojson.features.length} parcels into ${importCounty} — available offline.`)
    } catch (err) {
      setMsg(`Import failed: ${err.message}`)
    } finally {
      e.target.value = ''
    }
  }

  const list = counties.length ? counties : COUNTIES

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Settings</h2>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-2">County Parcel Data</h3>
        <ul className="divide-y divide-slate-100 mb-3">
          {list.map((c) => {
            const local = cached.find((x) => x.county === c.county)
            return (
              <li key={c.county} className="py-2 flex items-center justify-between text-sm">
                <span className="text-slate-700">{c.county_name}</span>
                <span className={local ? 'text-green-600' : 'text-slate-400'}>
                  {local ? 'Cached offline' : 'Not cached'}
                </span>
              </li>
            )
          })}
        </ul>
        {msg && <div className="mb-3"><Banner tone="info">{msg}</Banner></div>}
        <Button onClick={onSync} disabled={busy || !online} variant="secondary">
          <span className="inline-flex items-center justify-center gap-2">
            <RefreshCw size={16} /> {busy ? 'Starting sync…' : 'Sync from server'}
          </span>
        </Button>
        <p className="text-xs text-slate-400 mt-2">
          Automatic sync runs monthly on the 1st at 2:00 AM local time (spec §5.2).
        </p>
      </Card>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-2 inline-flex items-center gap-2">
          <Upload size={16} /> Import parcel data (offline)
        </h3>
        <p className="text-sm text-slate-500 mb-3">
          On WiFi, download a county’s parcel GeoJSON from its GIS portal, then load
          it here. It’s stored on the phone for fully offline lookup in the field.
        </p>
        <div className="flex items-center gap-2 mb-3">
          <select
            value={importCounty}
            onChange={(e) => setImportCounty(e.target.value)}
            className="rounded-xl border border-slate-300 px-3 py-2 text-sm"
          >
            {COUNTIES.map((c) => (
              <option key={c.county} value={c.county}>{c.county_name}</option>
            ))}
          </select>
          <label className="flex-1">
            <span className="sr-only">Choose GeoJSON</span>
            <input
              type="file"
              accept=".geojson,application/geo+json,application/json"
              onChange={onImport}
              className="block w-full text-sm"
            />
          </label>
        </div>
      </Card>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-1">Account</h3>
        <p className="text-sm text-slate-600">Signed in as {username || 'operator'}.</p>
      </Card>
    </div>
  )
}
