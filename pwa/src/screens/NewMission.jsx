import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, LocateFixed } from 'lucide-react'
import { useStore } from '../store/useStore'
import { geocode, lookupParcel } from '../api/client'
import { getCurrentPosition } from '../lib/geolocation'
import { lookupParcelOffline } from '../lib/offline/parcelLookup'
import { Button, Card, Field, TextInput, Banner } from '../components/ui'

// New Mission (spec §3.3) — two ways in:
//   1. "Use my location" — phone GPS (works fully offline), parcel looked up
//      against cached county data. Best for standing on the property.
//   2. Address search — geocoded online (cached for offline reuse).
// Parcel lookup always tries the on-device cache first so the field flow needs
// no server (spec §10.1).
export default function NewMission() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const setDraft = useStore((s) => s.setDraft)
  const online = useStore((s) => s.online)
  const [address, setAddress] = useState(draft.address || '')
  const [busy, setBusy] = useState('')
  const [err, setErr] = useState('')

  // Shared step: given a point, find its parcel (offline cache first).
  async function resolveParcel(lng, lat, countyHint) {
    let parcel = await lookupParcelOffline(lng, lat, countyHint || null)
    if (!parcel && online) {
      try {
        parcel = await lookupParcel(lat, lng, countyHint || undefined)
      } catch {
        /* fall through to the not-found message */
      }
    }
    if (!parcel) {
      throw new Error(
        'No parcel found here in your cached counties. Sync the county in Settings (on WiFi) before heading out.'
      )
    }
    setDraft({ parcel })
    navigate('/parcel')
  }

  async function onUseLocation() {
    setErr('')
    setBusy('gps')
    try {
      const { lat, lng, accuracy } = await getCurrentPosition()
      setDraft({
        address: draft.address || 'Current location',
        geocode: { lat, lng, county: null, county_name: null, source: 'device-gps', accuracy }
      })
      await resolveParcel(lng, lat, null)
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy('')
    }
  }

  async function onFindAddress(e) {
    e.preventDefault()
    setErr('')
    setBusy('addr')
    try {
      const g = await geocode(address) // online, or IndexedDB cache fallback
      setDraft({ address, geocode: g })
      if (!g.county) {
        setErr('Address is outside the supported counties (Blount, Knox, Sevier).')
      }
      await resolveParcel(g.lng, g.lat, g.county)
    } catch (e) {
      setErr(
        e?.message ||
          'Could not geocode that address. With no signal, use “Use my location” instead.'
      )
    } finally {
      setBusy('')
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">New Mission</h2>

      <Card>
        <p className="text-sm text-slate-600 mb-3">
          Standing on the property? Use your phone’s GPS — works with no signal.
        </p>
        <Button onClick={onUseLocation} disabled={!!busy}>
          <span className="inline-flex items-center justify-center gap-2">
            <LocateFixed size={18} /> {busy === 'gps' ? 'Locating…' : 'Use my location'}
          </span>
        </Button>
      </Card>

      <div className="text-center text-xs text-slate-400">— or —</div>

      <Card>
        <form onSubmit={onFindAddress}>
          <Field label="Property address" hint="Needs signal (or a previously searched address).">
            <TextInput
              placeholder="123 Main St, Maryville, TN"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              autoComplete="street-address"
            />
          </Field>
          <Button type="submit" variant="secondary" disabled={!!busy || !address.trim()}>
            <span className="inline-flex items-center justify-center gap-2">
              <Search size={18} /> {busy === 'addr' ? 'Locating…' : 'Find by address'}
            </span>
          </Button>
        </form>
      </Card>

      {!online && (
        <Banner tone="warn">
          Offline — GPS + cached parcels still work. Address search resumes on WiFi/LTE.
        </Banner>
      )}
      {err && <Banner tone="warn">{err}</Banner>}

      {draft.geocode && (
        <Card>
          <h3 className="font-semibold text-slate-700 mb-1">Location</h3>
          <p className="text-xs text-slate-400 mt-1">
            {draft.geocode.lat?.toFixed(6)}, {draft.geocode.lng?.toFixed(6)} · via{' '}
            {draft.geocode.source}
            {draft.geocode.accuracy ? ` · ±${Math.round(draft.geocode.accuracy)}m` : ''}
          </p>
        </Card>
      )}
    </div>
  )
}
