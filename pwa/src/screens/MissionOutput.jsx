import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plane, Share2, FolderInput } from 'lucide-react'
import { useStore } from '../store/useStore'
import { shareMissionBlob } from '../lib/dji'
import { Button, Card, Banner } from '../components/ui'

// Mission Output (spec §3.3, §3.4) — KMZ is generated on-device in DJI's WPML
// format. DJI Fly has no import button and never appears in the iOS share sheet,
// so the only path is to save the KMZ to Files and use it to replace a
// placeholder mission inside DJI Fly's own folder. No network required.
export default function MissionOutput() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const mission = draft.mission
  const kmzBlob = draft.kmzBlob
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  // A short, file-system-safe name the user can recognize when replacing the
  // placeholder. DJI's folder name still has to be matched manually (step 4).
  const missionName = `tncgas-${new Date(mission?.generatedAt || Date.now())
    .toISOString()
    .slice(0, 10)}`

  async function onShare() {
    setErr('')
    if (!kmzBlob) {
      setErr('Mission file is missing — regenerate it from the parcel preview.')
      return
    }
    try {
      const { method } = await shareMissionBlob(kmzBlob, missionName)
      if (method === 'cancelled') return
      setMsg(
        method === 'share-sheet'
          ? 'Choose AirDrop (to your Mac) or “Save to Files,” then run the installer.'
          : `Saved ${missionName}.kmz to your Downloads. Now run the installer below.`
      )
    } catch {
      setErr('Could not save the KMZ. Try again.')
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
      <Banner tone="success">Generated on-device — ready to fly with no signal.</Banner>

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
          <Share2 size={18} /> Save mission file (KMZ)
        </span>
      </Button>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-2 inline-flex items-center gap-2">
          <FolderInput size={16} /> Load onto your DJI RC 2
        </h3>
        <p className="text-xs text-slate-500 mb-2">
          Everyday flow — about 20 seconds once the one-time setup is done:
        </p>
        <ol className="list-decimal pl-5 space-y-1.5 text-sm text-slate-600">
          <li>Tap <b>Save mission file</b> above → <b>AirDrop</b> it to your Mac.</li>
          <li>Plug the <b>RC 2</b> into the Mac with USB-C.</li>
          <li>Double-click <b>“TNC GAS Installer”</b> on your Mac’s Desktop.</li>
          <li>Reopen <b>DJI Fly → Waypoint</b> on the RC 2 — your mission is loaded. Fly it.</li>
        </ol>
        <p className="text-xs text-slate-500 mt-3">
          First time only: set up the Mac helper (~10 min) —{' '}
          <a href="/tools/SETUP.txt" target="_blank" rel="noreferrer"
            className="text-gas-navy underline font-semibold">open setup guide</a>.
        </p>
        <p className="text-xs text-slate-400 mt-2">
          The installer auto-finds your AirDropped file and the right slot on the
          RC 2 — no renaming, no folder digging. (iPhone can’t write to the RC 2
          directly; the Mac is the required bridge.)
        </p>
      </Card>

      <Button variant="secondary" onClick={() => navigate('/upload')}>
        <span className="inline-flex items-center justify-center gap-2">
          <Plane size={18} /> After the flight → Upload images (on WiFi)
        </span>
      </Button>
    </div>
  )
}
