import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plane, Share2, Camera, Compass } from 'lucide-react'
import { useStore } from '../store/useStore'
import { shareMissionBlob } from '../lib/dji'
import { manualFlightSettings } from '../lib/offline/grid'
import { Button, Card, Banner } from '../components/ui'

// Mission Output — the primary flow is flying the grid BY HAND with the camera
// on a timed interval (works on any DJI controller, no mission import needed).
// A KMZ in DJI WPML format is also generated for phone-based controllers that
// can import it. Everything is produced on-device; no network required.
export default function MissionOutput() {
  const navigate = useNavigate()
  const draft = useStore((s) => s.draft)
  const mission = draft.mission
  const kmzBlob = draft.kmzBlob
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [showAuto, setShowAuto] = useState(false)

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
  const manual = manualFlightSettings(s.photo_spacing_ft || 20)

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Mission Ready</h2>
      <Banner tone="success">Flight plan ready — fly it by hand, no controller setup needed.</Banner>

      {/* HERO: set the camera */}
      <Card>
        <h3 className="font-semibold text-slate-700 mb-2 inline-flex items-center gap-2">
          <Camera size={16} /> 1 · Set the camera (once, before takeoff)
        </h3>
        <ul className="list-disc pl-5 space-y-1.5 text-sm text-slate-600">
          <li>Tilt the gimbal <b>straight down (−90°)</b> so the camera looks at the ground.</li>
          <li>Photo mode → <b>Timed Shot / Interval</b> → set to <b>every {manual.intervalSec} seconds</b>.</li>
          <li>Single photo per shot (not AEB/bracketing). JPEG is fine.</li>
        </ul>
      </Card>

      {/* HERO: fly the grid */}
      <Card>
        <h3 className="font-semibold text-slate-700 mb-2 inline-flex items-center gap-2">
          <Compass size={16} /> 2 · Fly the orange path
        </h3>
        <ul className="list-disc pl-5 space-y-1.5 text-sm text-slate-600">
          <li>Take off and climb to <b>{s.altitude_ft} ft</b>. Hold that altitude the whole flight.</li>
          <li>Fly the <b>{s.line_count} parallel passes</b> shown in orange, <b>{s.line_spacing_ft} ft</b> apart.</li>
          <li>Keep a slow, steady <b>~{manual.speedMph} mph</b> — the camera shoots every {manual.intervalSec}s on its own.</li>
          <li>Fly a few seconds <b>past each end</b> of the property so the edges are covered.</li>
          <li>Land when all passes are done. That’s it — you’ll have ~<b>{s.waypoints}</b> overlapping photos.</li>
        </ul>
        <p className="text-xs text-slate-400 mt-2">
          Tip: fly on a calm, well-lit day. Steady lines + that overlap = a clean map.
        </p>
      </Card>

      <Button onClick={() => navigate('/upload')}>
        <span className="inline-flex items-center justify-center gap-2">
          <Plane size={18} /> 3 · After the flight → Upload images (on WiFi)
        </span>
      </Button>

      {/* Secondary: automated controllers */}
      <button
        onClick={() => setShowAuto((v) => !v)}
        className="w-full text-left text-xs text-slate-400 underline"
      >
        {showAuto ? 'Hide' : 'Using a phone-based controller (RC-N2)? Export the mission file'}
      </button>
      {showAuto && (
        <Card>
          <p className="text-xs text-slate-500 mb-2">
            For controllers where DJI Fly runs on your phone (RC-N2) you can import
            this KMZ via the Files app. It does <b>not</b> work on the sealed RC 2.
          </p>
          {msg && <Banner tone="success">{msg}</Banner>}
          {err && <Banner tone="error">{err}</Banner>}
          <Button variant="secondary" onClick={onShare}>
            <span className="inline-flex items-center justify-center gap-2">
              <Share2 size={18} /> Save mission file (KMZ)
            </span>
          </Button>
        </Card>
      )}
    </div>
  )
}
