import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Map as MapIcon, Mountain, Printer, FileDown, Loader } from 'lucide-react'
import { useStore } from '../store/useStore'
import { createProject, renderMaps, projectMaps, downloadMapBlob } from '../api/client'
import { Button, Card, Banner } from '../components/ui'

// Map Viewer (spec §3.3, §9) — generate Map 1 (flat) + Map 2 (elevation) PDFs
// from the current parcel and download them. Rendering runs on the backend
// (spec §10.2 — requires connectivity); with just a parcel boundary the maps
// come out as scaled grid sheets, richer once WebODM ortho/DEM is attached.
export default function MapViewer() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const online = useStore((s) => s.online)
  const [busy, setBusy] = useState(false)
  const [ready, setReady] = useState(false)
  const [projectId, setProjectId] = useState(null)
  const [err, setErr] = useState('')

  async function onGenerate() {
    setErr('')
    if (!draft.parcel?.geojson) {
      setErr('No parcel loaded — locate a property first.')
      return
    }
    setBusy(true)
    try {
      const project = await createProject({
        address: draft.geocode?.address || draft.address || 'Untitled',
        county: draft.geocode?.county,
        lat: draft.geocode?.lat,
        lng: draft.geocode?.lng,
        parcel_id: draft.parcel?.parcel_id,
        parcel_geojson: draft.parcel?.geojson,
        use_case: 'both'
      })
      setProjectId(project.id)
      await renderMaps(project.id)
      // Poll until both PDFs are ready (local flag — `ready` state is stale here).
      let done = false
      for (let i = 0; i < 20 && !done; i++) {
        const maps = await projectMaps(project.id)
        if (maps.ready) {
          done = true
          setReady(true)
          break
        }
        await new Promise((r) => setTimeout(r, 1500))
      }
      if (!done) setErr('Rendering is taking longer than expected — try again shortly.')
    } catch (e) {
      setErr(e?.response?.data?.detail || 'Map generation failed (needs the server on WiFi).')
    } finally {
      setBusy(false)
    }
  }

  async function onDownload(kind) {
    try {
      const blob = await downloadMapBlob(projectId, kind)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${kind}-map.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch {
      setErr('Could not download that PDF yet.')
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Map Viewer</h2>

      {!draft.parcel?.geojson ? (
        <Banner tone="warn">
          No parcel loaded.{' '}
          <button className="underline" onClick={() => navigate('/new')}>Locate a property</button>.
        </Banner>
      ) : (
        <>
          {!online && <Banner tone="warn">Map rendering runs on the server — needs WiFi/LTE.</Banner>}

          <Card>
            <div className="flex items-center gap-2 text-slate-700 font-semibold mb-1">
              <MapIcon size={18} /> Map 1 — Flat Planning Map
            </div>
            <p className="text-sm text-slate-500">
              Grayscale ortho (when available) · bold parcel boundary · feature markers ·
              10 ft grid · scale bar · north arrow · title block (spec §9.1).
            </p>
            {ready && (
              <Button variant="secondary" className="mt-3" onClick={() => onDownload('flat')}>
                <span className="inline-flex items-center justify-center gap-2">
                  <FileDown size={16} /> Download Map 1 (PDF)
                </span>
              </Button>
            )}
          </Card>

          <Card>
            <div className="flex items-center gap-2 text-slate-700 font-semibold mb-1">
              <Mountain size={18} /> Map 2 — Elevation Change Map
            </div>
            <p className="text-sm text-slate-500">
              Hillshade + 1 ft/5 ft contours (with DSM/DTM) · slope · same markers ·
              grayscale, printer-safe (spec §9.2).
            </p>
            {ready && (
              <Button variant="secondary" className="mt-3" onClick={() => onDownload('elev')}>
                <span className="inline-flex items-center justify-center gap-2">
                  <FileDown size={16} /> Download Map 2 (PDF)
                </span>
              </Button>
            )}
          </Card>

          {err && <Banner tone="error">{err}</Banner>}
          {ready && <Banner tone="success">Maps rendered — download above or open Print/Export.</Banner>}

          {!ready && (
            <Button onClick={onGenerate} disabled={busy || !online}>
              <span className="inline-flex items-center justify-center gap-2">
                {busy ? <Loader size={18} className="animate-spin" /> : <Printer size={18} />}
                {busy ? 'Rendering…' : 'Generate maps'}
              </span>
            </Button>
          )}
        </>
      )}
    </div>
  )
}
