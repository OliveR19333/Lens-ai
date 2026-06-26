import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, RefreshCw, Database, Clock } from 'lucide-react'
import { useStore } from '../store/useStore'
import { listCounties, listProjects } from '../api/client'
import { getCachedCounties } from '../db/parcelCache'
import { Button, Card, Banner } from '../components/ui'

// Home / Dashboard (spec §3.3) — recent projects, sync status, county cache.
export default function Dashboard() {
  const navigate = useNavigate()
  const username = useStore((s) => s.username)
  const online = useStore((s) => s.online)
  const counties = useStore((s) => s.counties)
  const setCounties = useStore((s) => s.setCounties)
  const setSelectedProjectId = useStore((s) => s.setSelectedProjectId)
  const [cached, setCached] = useState([])
  const [recent, setRecent] = useState([])
  const [err, setErr] = useState('')

  useEffect(() => {
    getCachedCounties().then(setCached)
    if (online) {
      listCounties()
        .then(setCounties)
        .catch(() => setErr('Could not reach the server — showing cached data.'))
      listProjects().then((p) => setRecent(p.slice(0, 5))).catch(() => {})
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [online])

  const cacheFor = (key) => cached.find((c) => c.county === key)

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-800">Welcome{username ? `, ${username}` : ''}</h2>
        <p className="text-slate-500 text-sm">Start a mission or review county data.</p>
      </div>

      {err && <Banner tone="warn">{err}</Banner>}

      <Button onClick={() => navigate('/new')}>
        <span className="inline-flex items-center justify-center gap-2">
          <Plus size={18} /> New Mission
        </span>
      </Button>

      <Card>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-700 inline-flex items-center gap-2">
            <Database size={16} /> County Cache
          </h3>
          <button
            onClick={() => navigate('/settings')}
            className="text-gas-navy text-sm inline-flex items-center gap-1"
          >
            <RefreshCw size={14} /> Sync
          </button>
        </div>
        <ul className="divide-y divide-slate-100">
          {(counties.length
            ? counties
            : [{ county: 'blount', county_name: 'Blount County' },
               { county: 'knox', county_name: 'Knox County' },
               { county: 'sevier', county_name: 'Sevier County' }]
          ).map((c) => {
            const local = cacheFor(c.county)
            return (
              <li key={c.county} className="py-2 flex items-center justify-between text-sm">
                <span className="text-slate-700">{c.county_name}</span>
                <span className={local ? 'text-green-600' : 'text-slate-400'}>
                  {local ? 'Cached offline' : c.version_hash ? 'Available' : 'Not synced'}
                </span>
              </li>
            )
          })}
        </ul>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-700 inline-flex items-center gap-2">
            <Clock size={16} /> Recent Projects
          </h3>
          <button onClick={() => navigate('/history')} className="text-gas-navy text-sm">
            View all
          </button>
        </div>
        {recent.length === 0 ? (
          <p className="text-slate-400 text-sm">No projects yet — create a mission to begin.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {recent.map((p) => (
              <li
                key={p.id}
                className="py-2 text-sm cursor-pointer"
                onClick={() => {
                  setSelectedProjectId(p.id)
                  navigate('/annotate')
                }}
              >
                <div className="text-slate-700 truncate">{p.address}</div>
                <div className="text-xs text-slate-400">
                  {new Date(p.created_at).toLocaleDateString()} · {p.status}
                  {p.print_scale ? ` · ${p.print_scale}` : ''}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
