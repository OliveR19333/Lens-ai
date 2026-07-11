import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2, MapPin } from 'lucide-react'
import { useStore } from '../store/useStore'
import { getProject, getAnnotations, addAnnotation, deleteAnnotation } from '../api/client'
import { Card, Banner, Button } from '../components/ui'
import ParcelMap from '../components/ParcelMap'

const TYPES = ['pond', 'trees', 'structure', 'driveway', 'fence', 'note']

// Manual annotation layer (spec §12) — tap the map to drop a typed marker.
export default function Annotate() {
  const navigate = useNavigate()
  const projectId = useStore((s) => s.selectedProjectId)
  const [project, setProject] = useState(null)
  const [annotations, setAnnotations] = useState({ features: [] })
  const [type, setType] = useState('pond')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!projectId) return
    getProject(projectId).then(setProject).catch(() => setErr('Could not load project.'))
    getAnnotations(projectId).then((r) => setAnnotations(r.annotations)).catch(() => {})
  }, [projectId])

  const markers = useMemo(
    () =>
      (annotations.features || [])
        .filter((f) => f.geometry?.type === 'Point')
        .map((f) => ({
          lng: f.geometry.coordinates[0],
          lat: f.geometry.coordinates[1],
          label: f.properties?.label,
          id: f.properties?.id
        })),
    [annotations]
  )

  async function onPick([lng, lat]) {
    if (!projectId) return
    setBusy(true)
    setErr('')
    try {
      const r = await addAnnotation(projectId, type, { type: 'Point', coordinates: [lng, lat] })
      setAnnotations(r.annotations)
    } catch {
      setErr('Could not save marker (needs the server).')
    } finally {
      setBusy(false)
    }
  }

  async function onDelete(id) {
    const r = await deleteAnnotation(projectId, id)
    setAnnotations(r.annotations)
  }

  if (!projectId) {
    return (
      <div className="p-4">
        <Banner tone="warn">
          Pick a project to annotate from{' '}
          <button className="underline" onClick={() => navigate('/history')}>History</button>.
        </Banner>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Annotate</h2>
      {project && <p className="text-sm text-slate-500 -mt-2">{project.address}</p>}

      <Card>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-sm text-slate-600">Marker type:</span>
          <select value={type} onChange={(e) => setType(e.target.value)}
            className="rounded-xl border border-slate-300 px-3 py-2 text-sm">
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          {busy && <span className="text-xs text-slate-400">saving…</span>}
        </div>
        {project?.parcel_geojson ? (
          <ParcelMap
            geojson={project.parcel_geojson}
            center={project.lng != null ? [project.lng, project.lat] : undefined}
            markers={markers}
            onPick={onPick}
            height={320}
          />
        ) : (
          <Banner tone="info">No parcel boundary on this project to annotate.</Banner>
        )}
        <p className="text-xs text-slate-400 mt-2">Tap the map to drop a {type} marker.</p>
      </Card>

      {err && <Banner tone="error">{err}</Banner>}

      <Card>
        <h3 className="font-semibold text-slate-700 mb-2">Markers ({markers.length})</h3>
        {markers.length === 0 ? (
          <p className="text-sm text-slate-400">None yet.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {markers.map((m) => (
              <li key={m.id} className="py-2 flex items-center justify-between text-sm">
                <span className="text-slate-700 inline-flex items-center gap-2">
                  <MapPin size={14} /> {m.label}
                </span>
                <button onClick={() => onDelete(m.id)} className="text-red-500" aria-label="Delete">
                  <Trash2 size={16} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Banner tone="info">Markers appear on both maps next time you generate them (spec §9/§12).</Banner>
    </div>
  )
}
