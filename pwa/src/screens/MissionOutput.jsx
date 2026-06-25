import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plane, Share2 } from 'lucide-react'
import { useStore } from '../store/useStore'
import { shareMissionKmz } from '../lib/dji'
import { Button, Card, Banner } from '../components/ui'

// Mission Output (spec §3.3, §3.4) — KMZ download + DJI Fly share handoff.
export default function MissionOutput() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const token = useStore((s) => s.token)
  const mission = draft.mission
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  async function onShare() {
    setErr('')
    try {
      const { method } = await shareMissionKmz(mission.mission_id, token)
      setMsg(
        method === 'share-sheet'
          ? 'Share sheet opened — choose “Copy to DJI Fly” or save to Files.'
          : 'KMZ downloaded — open Files and import into DJI Fly.'
      )
    } catch {
      setErr('Could not share the KMZ. Try again on WiFi/LTE.')
    }
  }

  if (!mission) {
    return (
      <div className="p-4">
        <Banner tone="warn">
          No mission yet.{' '}
          <button className="underline" onClick={() => navigate('/new')}>Start one</button>.
        </Banner>
      </div>
    )
  }

  const s = mission.summary || {}

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Mission Ready</h2>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-2">Flight plan summary</h3>
        <dl className="grid grid-cols-2 gap-y-2 text-sm">
          <dt className="text-slate-500">Waypoints</dt><dd className="text-right">{s.waypoints}</dd>
          <dt className="text-slate-500">Flight lines</dt><dd className="text-right">{s.line_count}</dd>
          <dt className="text-slate-500">Line spacing</dt><dd className="text-right">{s.line_spacing_ft} ft</dd>
          <dt className="text-slate-500">Photo spacing</dt><dd className="text-right">{s.photo_spacing_ft} ft</dd>
          <dt className="text-slate-500">Altitude</dt><dd className="text-right">{s.altitude_ft} ft AGL</dd>
          <dt className="text-slate-500">Axis</dt><dd className="text-right">{s.flight_axis}</dd>
        </dl>
      </Card>

      {msg && <Banner tone="success">{msg}</Banner>}
      {err && <Banner tone="error">{err}</Banner>}

      <Button onClick={onShare}>
        <span className="inline-flex items-center justify-center gap-2">
          <Share2 size={18} /> Send to DJI Fly (KMZ)
        </span>
      </Button>

      <Banner tone="info">
        Tip: full app-to-app DJI transfer isn’t public — the share sheet (Copy to
        DJI Fly / Files) is the reliable path (spec §3.4).
      </Banner>

      <Button variant="secondary" onClick={() => navigate('/upload')}>
        <span className="inline-flex items-center justify-center gap-2">
          <Plane size={18} /> After the flight → Upload images
        </span>
      </Button>
    </div>
  )
}
