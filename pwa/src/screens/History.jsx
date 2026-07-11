import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Archive, ArchiveRestore, MapPin, PenLine } from 'lucide-react'
import { useStore } from '../store/useStore'
import { listProjects, setProjectArchived } from '../api/client'
import { Card, Banner, Button } from '../components/ui'

// Project history & archive (spec §3.3 / §12).
export default function History() {
  const navigate = useNavigate()
  const online = useStore((s) => s.online)
  const setSelectedProjectId = useStore((s) => s.setSelectedProjectId)
  const [projects, setProjects] = useState([])
  const [showArchived, setShowArchived] = useState(false)
  const [err, setErr] = useState('')

  async function load() {
    try {
      setProjects(await listProjects(showArchived))
    } catch {
      setErr('Could not load projects — needs the server on WiFi.')
    }
  }

  useEffect(() => {
    if (online) load()
    else setErr('Offline — project history lives on the server.')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [online, showArchived])

  async function toggleArchive(p) {
    await setProjectArchived(p.id, !p.archived)
    load()
  }

  function annotate(p) {
    setSelectedProjectId(p.id)
    navigate('/annotate')
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Project History</h2>
        <label className="text-sm text-slate-500 inline-flex items-center gap-2">
          <input type="checkbox" checked={showArchived} onChange={(e) => setShowArchived(e.target.checked)} />
          Show archived
        </label>
      </div>

      {err && <Banner tone="warn">{err}</Banner>}

      {projects.length === 0 && !err && (
        <Card><p className="text-sm text-slate-400">No projects yet.</p></Card>
      )}

      {projects.map((p) => (
        <Card key={p.id}>
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="font-semibold text-slate-700 truncate">{p.address}</div>
              <div className="text-xs text-slate-400 mt-0.5">
                {new Date(p.created_at).toLocaleDateString()} · {p.county || '—'} · {p.status}
                {p.print_scale ? ` · ${p.print_scale}` : ''}
                {p.archived ? ' · archived' : ''}
              </div>
            </div>
          </div>
          <div className="flex gap-2 mt-3">
            <Button variant="secondary" className="!py-2" onClick={() => annotate(p)}>
              <span className="inline-flex items-center justify-center gap-1 text-sm"><PenLine size={14} /> Annotate</span>
            </Button>
            <Button variant="ghost" className="!py-2" onClick={() => toggleArchive(p)}>
              <span className="inline-flex items-center justify-center gap-1 text-sm">
                {p.archived ? <ArchiveRestore size={14} /> : <Archive size={14} />}
                {p.archived ? 'Unarchive' : 'Archive'}
              </span>
            </Button>
          </div>
        </Card>
      ))}

      <Button variant="ghost" onClick={() => navigate('/new')}>
        <span className="inline-flex items-center justify-center gap-2"><MapPin size={16} /> New mission</span>
      </Button>
    </div>
  )
}
