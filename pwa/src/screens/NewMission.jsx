import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import { useStore } from '../store/useStore'
import { geocode, lookupParcel } from '../api/client'
import { Button, Card, Field, TextInput, Banner } from '../components/ui'

// New Mission (spec §3.3) — address input → geocode → parcel lookup → preview.
export default function NewMission() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const setDraft = useStore((s) => s.setDraft)
  const [address, setAddress] = useState(draft.address || '')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  async function onFind(e) {
    e.preventDefault()
    setErr('')
    setBusy(true)
    try {
      const g = await geocode(address)
      setDraft({ address, geocode: g })
      if (!g.county) {
        setErr(
          `Address geocoded, but it is outside the supported counties (Blount, Knox, Sevier).`
        )
      }
      // Try to pull the parcel boundary right away.
      try {
        const parcel = await lookupParcel(g.lat, g.lng, g.county || undefined)
        setDraft({ parcel })
        navigate('/parcel')
      } catch {
        setErr(
          (prev) =>
            prev ||
            'No cached parcel found for this point. Sync the county in Settings, then retry.'
        )
      }
    } catch {
      setErr('Could not geocode that address. Check the spelling or your connection.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">New Mission</h2>

      <Card>
        <form onSubmit={onFind}>
          <Field label="Property address" hint="Geocoded via US Census (offline-cached when available).">
            <TextInput
              placeholder="123 Main St, Maryville, TN"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              autoComplete="street-address"
              required
            />
          </Field>
          <Button type="submit" disabled={busy || !address.trim()}>
            <span className="inline-flex items-center justify-center gap-2">
              <Search size={18} /> {busy ? 'Locating…' : 'Find parcel'}
            </span>
          </Button>
        </form>
      </Card>

      {err && <Banner tone="warn">{err}</Banner>}

      {draft.geocode && (
        <Card>
          <h3 className="font-semibold text-slate-700 mb-1">Geocode result</h3>
          <p className="text-sm text-slate-600">{draft.geocode.address}</p>
          <p className="text-xs text-slate-400 mt-1">
            {draft.geocode.lat?.toFixed(6)}, {draft.geocode.lng?.toFixed(6)} ·{' '}
            {draft.geocode.county_name || 'Unsupported county'} · via {draft.geocode.source}
            {draft.geocode._offline ? ' (offline cache)' : ''}
          </p>
        </Card>
      )}
    </div>
  )
}
