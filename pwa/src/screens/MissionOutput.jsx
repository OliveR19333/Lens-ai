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
      setMsg(
        method === 'share-sheet'
          ? 'Tap “Save to Files”, then follow the import steps below.'
          : 'KMZ saved. Open the Files app and follow the import steps below.'
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
          <FolderInput size={16} /> Get it into DJI Fly
        </h3>
        <p className="text-xs text-slate-500 mb-2">
          DJI Fly has no “import” button, so you swap this file in for a blank
          placeholder mission. You only set this up once per flight.
        </p>
        <ol className="list-decimal pl-5 space-y-1.5 text-sm text-slate-600">
          <li>Tap <b>Save mission file</b> above → <b>Save to Files</b> → <b>On My iPhone</b>.</li>
          <li>
            Open <b>DJI Fly</b> → <b>Waypoint</b> mode → create a <b>new</b> mission,
            drop one dummy point anywhere, and <b>save</b> it. (This makes the folder
            we’ll drop into.)
          </li>
          <li>
            Open the <b>Files</b> app → <b>On My iPhone</b> → <b>DJI Fly</b> →
            <b> wayline_mission</b>, and open the <b>newest</b> numbered folder.
          </li>
          <li>
            Note the <b>.kmz</b> filename inside it. Rename your saved
            <b> {missionName}.kmz</b> to that <b>exact</b> name and move it into
            that folder, replacing the file.
          </li>
          <li>Reopen <b>DJI Fly → Waypoint</b>. Your mapping grid is now the mission. Fly it.</li>
        </ol>
        <p className="text-xs text-slate-400 mt-2">
          Flying with a DJI RC controller (built-in screen)? The same{' '}
          <b>wayline_mission</b> folder lives on the controller — connect it to a
          computer to do the swap.
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
