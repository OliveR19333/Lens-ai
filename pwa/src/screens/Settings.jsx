import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { useStore } from '../store/useStore'
import { listCounties, syncParcels } from '../api/client'
import { getCachedCounties } from '../db/parcelCache'
import { Button, Card, Banner } from '../components/ui'

// Settings (spec §3.3) — county selection, monthly sync schedule, account.
export default function Settings() {
  const username = useStore((s) => s.username)
  const online = useStore((s) => s.online)
  const counties = useStore((s) => s.counties)
  const setCounties = useStore((s) => s.setCounties)
  const [cached, setCached] = useState([])
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    getCachedCounties().then(setCached)
    if (online) listCounties().then(setCounties).catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [online])

  async function onSync() {
    setBusy(true)
    setMsg('')
    try {
      const res = await syncParcels()
      setMsg(res.message || 'Parcel sync started.')
    } catch {
      setMsg('Could not start sync — server unreachable.')
    } finally {
      setBusy(false)
    }
  }

  const list = counties.length
    ? counties
    : [
        { county: 'blount', county_name: 'Blount County' },
        { county: 'knox', county_name: 'Knox County' },
        { county: 'sevier', county_name: 'Sevier County' }
      ]

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Settings</h2>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-2">County Parcel Data</h3>
        <ul className="divide-y divide-slate-100 mb-3">
          {list.map((c) => {
            const local = cached.find((x) => x.county === c.county)
            return (
              <li key={c.county} className="py-2 flex items-center justify-between text-sm">
                <span className="text-slate-700">{c.county_name}</span>
                <span className={local ? 'text-green-600' : 'text-slate-400'}>
                  {local ? 'Cached offline' : 'Not cached'}
                </span>
              </li>
            )
          })}
        </ul>
        {msg && <div className="mb-3"><Banner tone="info">{msg}</Banner></div>}
        <Button onClick={onSync} disabled={busy || !online} variant="secondary">
          <span className="inline-flex items-center justify-center gap-2">
            <RefreshCw size={16} /> {busy ? 'Starting sync…' : 'Sync parcels now'}
          </span>
        </Button>
        <p className="text-xs text-slate-400 mt-2">
          Automatic sync runs monthly on the 1st at 2:00 AM local time (spec §5.2).
        </p>
      </Card>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-1">Account</h3>
        <p className="text-sm text-slate-600">Signed in as {username || 'operator'}.</p>
      </Card>
    </div>
  )
}
