import { useState } from 'react'
import { Upload as UploadIcon, Video, Images } from 'lucide-react'
import { useStore } from '../store/useStore'
import { createProject, uploadImages, uploadVideo } from '../api/client'
import { Button, Card, Banner, Field } from '../components/ui'

// Post-flight upload: send a flight VIDEO (frames extracted server-side) or a
// set of photos → WebODM processing. Needs WiFi/LTE (files are large).
export default function UploadImages() {
  const draft = useStore((s) => s.draft)
  const online = useStore((s) => s.online)
  const [mode, setMode] = useState('video') // 'video' | 'photos'
  const [files, setFiles] = useState([])
  const [video, setVideo] = useState(null)
  const [fps, setFps] = useState(1)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')

  const ready = mode === 'video' ? !!video : files.length > 0

  async function onUpload() {
    setErr('')
    setResult(null)
    setBusy(true)
    try {
      // Ensure a project exists to attach the imagery to.
      const project = await createProject({
        address: draft.geocode?.address || draft.address || 'Untitled',
        county: draft.geocode?.county,
        lat: draft.geocode?.lat,
        lng: draft.geocode?.lng,
        parcel_id: draft.parcel?.parcel_id,
        parcel_geojson: draft.parcel?.geojson,
        use_case: 'both'
      })
      const res =
        mode === 'video'
          ? await uploadVideo(project.id, video, fps)
          : await uploadImages(project.id, files)
      setResult({ projectId: project.id, ...res })
    } catch (e) {
      setErr(e?.response?.data?.detail || 'Upload failed. WiFi/LTE is required and the file may be large.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Upload Flight</h2>

      {!online && (
        <Banner tone="warn">You’re offline. Uploading to WebODM needs WiFi/LTE.</Banner>
      )}

      {/* Video vs photos toggle */}
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => setMode('video')}
          className={`rounded-xl border p-3 text-sm font-medium inline-flex items-center justify-center gap-2 ${
            mode === 'video' ? 'border-gas-navy bg-gas-sky text-gas-navy' : 'border-slate-200 text-slate-500'
          }`}
        >
          <Video size={16} /> Flight video
        </button>
        <button
          onClick={() => setMode('photos')}
          className={`rounded-xl border p-3 text-sm font-medium inline-flex items-center justify-center gap-2 ${
            mode === 'photos' ? 'border-gas-navy bg-gas-sky text-gas-navy' : 'border-slate-200 text-slate-500'
          }`}
        >
          <Images size={16} /> Photos
        </button>
      </div>

      {mode === 'video' ? (
        <Card>
          <label className="block">
            <span className="block text-sm font-medium text-slate-700 mb-2">
              Select the flight video
            </span>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setVideo(e.target.files?.[0] || null)}
              className="block w-full text-sm"
            />
          </label>
          {video && (
            <p className="text-xs text-slate-500 mt-2">
              {video.name} · {(video.size / 1e6).toFixed(0)} MB
            </p>
          )}
          <div className="mt-3">
            <Field
              label={`Frames per second: ${fps}`}
              hint="1 fps is plenty for mapping. Higher = more frames, longer processing."
            >
              <input
                type="range" min="0.5" max="2" step="0.5" value={fps}
                onChange={(e) => setFps(Number(e.target.value))} className="w-full"
              />
            </Field>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            We pull still frames from the video on the server — continuous video means no
            coverage gaps. Record with the camera pointed straight down.
          </p>
        </Card>
      ) : (
        <Card>
          <label className="block">
            <span className="block text-sm font-medium text-slate-700 mb-2">
              Select images from the flight
            </span>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => setFiles(Array.from(e.target.files || []))}
              className="block w-full text-sm"
            />
          </label>
          {files.length > 0 && (
            <p className="text-xs text-slate-500 mt-2">{files.length} image(s) selected.</p>
          )}
        </Card>
      )}

      {err && <Banner tone="error">{err}</Banner>}
      {result && (
        <Banner tone="success">
          {result.message || 'Queued for processing.'} Project {result.projectId?.slice(0, 8)}.
        </Banner>
      )}

      <Button onClick={onUpload} disabled={busy || !ready || !online}>
        <span className="inline-flex items-center justify-center gap-2">
          <UploadIcon size={18} />
          {busy
            ? mode === 'video'
              ? 'Uploading video…'
              : 'Uploading…'
            : 'Push to WebODM'}
        </span>
      </Button>

      {busy && mode === 'video' && (
        <p className="text-xs text-slate-400 text-center">
          Large videos take a few minutes to upload — keep this screen open.
        </p>
      )}
    </div>
  )
}
