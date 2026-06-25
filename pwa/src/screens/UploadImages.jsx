import { useState } from 'react'
import { Upload as UploadIcon } from 'lucide-react'
import { useStore } from '../store/useStore'
import { createProject, uploadImages } from '../api/client'
import { Button, Card, Banner } from '../components/ui'

// Upload Images (spec §3.3) — post-flight: select images → WebODM queue.
// Requires connectivity (spec §10.2 — files too large for the offline queue).
export default function UploadImages() {
  const draft = useStore((s) => s.draft)
  const online = useStore((s) => s.online)
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')

  async function onUpload() {
    setErr('')
    setBusy(true)
    try {
      // Ensure a project exists to attach the images to.
      const project = await createProject({
        address: draft.geocode?.address || draft.address || 'Untitled',
        county: draft.geocode?.county,
        lat: draft.geocode?.lat,
        lng: draft.geocode?.lng,
        parcel_id: draft.parcel?.parcel_id,
        parcel_geojson: draft.parcel?.geojson,
        use_case: 'both'
      })
      const res = await uploadImages(project.id, files)
      setResult({ projectId: project.id, ...res })
    } catch (e) {
      setErr(e?.response?.data?.detail || 'Upload failed. WiFi/LTE is required (spec §10.2).')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Upload Drone Images</h2>

      {!online && (
        <Banner tone="warn">You’re offline. Image upload to WebODM needs WiFi/LTE.</Banner>
      )}

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

      {err && <Banner tone="error">{err}</Banner>}
      {result && (
        <Banner tone="success">
          Queued {result.message ? '' : ''}for processing. Project {result.projectId?.slice(0, 8)} —
          WebODM task {result.webodm_task_id || 'pending'}.
        </Banner>
      )}

      <Button onClick={onUpload} disabled={busy || files.length === 0 || !online}>
        <span className="inline-flex items-center justify-center gap-2">
          <UploadIcon size={18} /> {busy ? 'Uploading…' : 'Push to WebODM'}
        </span>
      </Button>
    </div>
  )
}
