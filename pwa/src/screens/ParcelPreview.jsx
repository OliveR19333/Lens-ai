import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Ruler, MousePointerClick, Plane } from 'lucide-react'
import { useStore } from '../store/useStore'
import { lookupParcel } from '../api/client'
import { lookupParcelOffline } from '../lib/offline/parcelLookup'
import { buildMissionKmz } from '../lib/offline/mission'
import { planGrid, manualFlightSettings } from '../lib/offline/grid'
import { computePrintScale } from '../lib/offline/scale'
import { Button, Card, Field, Banner } from '../components/ui'
import ParcelMap from '../components/ParcelMap'

// Parcel Preview (spec §3.3) — confirm boundary, see the measurements, set
// flight params, and generate the KMZ entirely on-device (offline, spec §10.1).
export default function ParcelPreview() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const setDraft = useStore((s) => s.setDraft)

  const online = useStore((s) => s.online)
  const [altitudeFt, setAltitudeFt] = useState(120)
  const [forwardOverlap, setForwardOverlap] = useState(80)
  const [sideOverlap, setSideOverlap] = useState(75)
  const [busy, setBusy] = useState(false)
  const [picking, setPicking] = useState(false)
  const [note, setNote] = useState('')
  const [err, setErr] = useState('')

  const parcelGeojson = draft.parcel?.geojson
  const center = draft.geocode ? [draft.geocode.lng, draft.geocode.lat] : undefined

  // Geocoders interpolate along the street, so the boundary can land on a
  // neighbor. Tapping the actual property re-runs point-in-polygon at that exact
  // spot and snaps the boundary to the right lot (cache first, then server).
  async function onPick([lng, lat]) {
    setErr('')
    setNote('')
    setPicking(true)
    try {
      const hint = draft.parcel?.county || draft.geocode?.county || null
      let parcel = await lookupParcelOffline(lng, lat, hint)
      if (!parcel && online) {
        try {
          parcel = await lookupParcel(lat, lng, hint || undefined)
        } catch {
          /* fall through */
        }
      }
      if (!parcel) {
        setNote('No parcel at that spot — tap directly on the property.')
        return
      }
      setDraft({ parcel, geocode: { ...(draft.geocode || {}), lat, lng, source: 'map-tap' } })
      setNote('Boundary updated to the property you tapped.')
    } finally {
      setPicking(false)
    }
  }

  // Measuring readout — computed on-device, instantly, offline (spec §9.3).
  const measure = useMemo(() => {
    if (!parcelGeojson) return null
    try {
      return computePrintScale(parcelGeojson)
    } catch {
      return null
    }
  }, [parcelGeojson])

  // Live flight plan — recomputed as the sliders move so the path on the map and
  // the hand-flying settings stay in sync.
  const plan = useMemo(() => {
    if (!parcelGeojson) return null
    try {
      return planGrid(parcelGeojson, {
        altitudeFt,
        forwardOverlap: forwardOverlap / 100,
        sideOverlap: sideOverlap / 100
      })
    } catch {
      return null
    }
  }, [parcelGeojson, altitudeFt, forwardOverlap, sideOverlap])

  const flightPath = useMemo(() => {
    if (!plan?.waypoints?.length) return null
    return {
      type: 'Feature',
      properties: {},
      geometry: { type: 'LineString', coordinates: plan.waypoints.map((w) => [w.lng, w.lat]) }
    }
  }, [plan])

  const manual = useMemo(() => (plan ? manualFlightSettings(plan.photoSpacingFt) : null), [plan])

  async function onGenerate() {
    if (!parcelGeojson) {
      setErr('No parcel boundary loaded. Go back and locate a property.')
      return
    }
    setErr('')
    setBusy(true)
    try {
      const result = await buildMissionKmz(parcelGeojson, {
        altitudeFt,
        forwardOverlap: forwardOverlap / 100,
        sideOverlap: sideOverlap / 100
      })
      // Keep the on-device blob for the share-sheet handoff.
      setDraft({
        mission: { summary: result.summary, scale: result.scale, generatedAt: Date.now() },
        kmzBlob: result.kmzBlob
      })
      navigate('/mission')
    } catch (e) {
      setErr(e?.message || 'Mission generation failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Parcel Preview</h2>

      {!parcelGeojson ? (
        <Banner tone="warn">
          No parcel loaded.{' '}
          <button className="underline" onClick={() => navigate('/new')}>Locate a property</button>.
        </Banner>
      ) : (
        <>
          <Banner tone="info">
            <span className="inline-flex items-center gap-2">
              <MousePointerClick size={16} />
              Wrong lot? Tap the correct property to snap the boundary. The orange
              line is the path to fly.
            </span>
          </Banner>

          <Card className="p-0 overflow-hidden">
            <ParcelMap geojson={parcelGeojson} center={center} onPick={onPick}
              flightPath={flightPath} height={360} />
          </Card>

          {picking && <p className="text-xs text-slate-400">Finding parcel…</p>}
          {note && <Banner tone="info">{note}</Banner>}

          {measure && (
            <Card>
              <h3 className="font-semibold text-slate-700 mb-2 inline-flex items-center gap-2">
                <Ruler size={16} /> Measurements
              </h3>
              <dl className="grid grid-cols-2 gap-y-1 text-sm">
                <dt className="text-slate-500">Width</dt>
                <dd className="text-right">{measure.parcelWidthFt} ft</dd>
                <dt className="text-slate-500">Height</dt>
                <dd className="text-right">{measure.parcelHeightFt} ft</dd>
                <dt className="text-slate-500">Area</dt>
                <dd className="text-right">
                  {measure.parcelAreaSqft.toLocaleString()} ft² ({measure.parcelAreaAcres} ac)
                </dd>
                <dt className="text-slate-500">Print scale</dt>
                <dd className="text-right">{measure.label}</dd>
              </dl>
              <p className="text-xs text-slate-400 mt-2">{measure.note}</p>
            </Card>
          )}

          <Card>
            <h3 className="font-semibold text-slate-700 mb-2">Flight settings</h3>
            <Field label={`Altitude: ${altitudeFt} ft AGL`} hint="120 ft is ideal for property mapping.">
              <input type="range" min="80" max="200" step="5" value={altitudeFt}
                onChange={(e) => setAltitudeFt(Number(e.target.value))} className="w-full" />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label={`Forward overlap: ${forwardOverlap}%`}>
                <input type="range" min="60" max="90" value={forwardOverlap}
                  onChange={(e) => setForwardOverlap(Number(e.target.value))} className="w-full" />
              </Field>
              <Field label={`Side overlap: ${sideOverlap}%`}>
                <input type="range" min="60" max="90" value={sideOverlap}
                  onChange={(e) => setSideOverlap(Number(e.target.value))} className="w-full" />
              </Field>
            </div>
            {plan && manual && (
              <p className="text-xs text-slate-500 mt-1">
                {plan.lineCount} passes · {plan.lineSpacingFt} ft apart · fly ~{manual.speedMph} mph ·
                photo every {manual.intervalSec}s
              </p>
            )}
          </Card>

          {err && <Banner tone="error">{err}</Banner>}

          <Button onClick={onGenerate} disabled={busy}>
            <span className="inline-flex items-center justify-center gap-2">
              <Plane size={18} /> {busy ? 'Building flight plan…' : 'Confirm & view flight plan'}
            </span>
          </Button>
        </>
      )}
    </div>
  )
}
