import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { generateMission } from '../api/client'
import { Button, Card, Field, TextInput, Banner } from '../components/ui'
import ParcelMap from '../components/ParcelMap'

// Parcel Preview (spec §3.3) — confirm boundary + flight params before fly.
export default function ParcelPreview() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const setDraft = useStore((s) => s.setDraft)

  const [altitudeFt, setAltitudeFt] = useState(120)
  const [forwardOverlap, setForwardOverlap] = useState(80)
  const [sideOverlap, setSideOverlap] = useState(75)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const parcelGeojson = draft.parcel?.geojson
  const center = draft.geocode ? [draft.geocode.lng, draft.geocode.lat] : undefined

  async function onGenerate() {
    if (!parcelGeojson) {
      setErr('No parcel boundary loaded. Go back and search an address.')
      return
    }
    setErr('')
    setBusy(true)
    try {
      const mission = await generateMission(parcelGeojson, {
        altitudeFt,
        forwardOverlap: forwardOverlap / 100,
        sideOverlap: sideOverlap / 100
      })
      setDraft({ mission })
      navigate('/mission')
    } catch (e) {
      setErr(e?.response?.data?.detail || 'Mission generation failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Parcel Preview</h2>

      {!parcelGeojson ? (
        <Banner tone="warn">
          No parcel loaded. <button className="underline" onClick={() => navigate('/new')}>Search an address</button>.
        </Banner>
      ) : (
        <>
          <Card className="p-0 overflow-hidden">
            <ParcelMap geojson={parcelGeojson} center={center} />
          </Card>

          <Card>
            <h3 className="font-semibold text-slate-700 mb-2">Flight settings (spec §6.1)</h3>
            <Field label={`Altitude: ${altitudeFt} ft AGL`} hint="Adjustable 80–200 ft.">
              <input
                type="range"
                min="80"
                max="200"
                step="5"
                value={altitudeFt}
                onChange={(e) => setAltitudeFt(Number(e.target.value))}
                className="w-full"
              />
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
          </Card>

          {err && <Banner tone="error">{err}</Banner>}

          <Button onClick={onGenerate} disabled={busy}>
            {busy ? 'Generating KMZ…' : 'Confirm & generate mission'}
          </Button>
        </>
      )}
    </div>
  )
}
