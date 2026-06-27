import { NavLink, useNavigate } from 'react-router-dom'
import { Home, MapPin, Clock, Map, Settings as SettingsIcon, LogOut } from 'lucide-react'
import { useStore } from '../store/useStore'

function OnlineBadge() {
  const online = useStore((s) => s.online)
  const queueDepth = useStore((s) => s.queueDepth)
  return (
    <span
      className={`text-xs px-2 py-1 rounded-full ${
        online ? 'bg-green-500/20 text-green-200' : 'bg-amber-500/20 text-amber-200'
      }`}
    >
      {online ? 'Online' : 'Offline'}
      {queueDepth > 0 && ` · ${queueDepth} queued`}
    </span>
  )
}

const tabs = [
  { to: '/', icon: Home, label: 'Home', end: true },
  { to: '/new', icon: MapPin, label: 'Mission' },
  { to: '/maps', icon: Map, label: 'Maps' },
  { to: '/history', icon: Clock, label: 'History' },
  { to: '/settings', icon: SettingsIcon, label: 'Settings' }
]

export default function Layout({ children }) {
  const navigate = useNavigate()
  const logout = useStore((s) => s.logout)

  return (
    <div className="flex flex-col h-full bg-slate-50">
      <header className="bg-gas-navy text-white px-4 py-3 flex items-center justify-between shadow">
        <div className="flex items-center gap-2">
          <img src="/logo.png" alt="" className="w-7 h-7 rounded" />
          <span className="font-semibold tracking-wide">TNC GAS</span>
        </div>
        <div className="flex items-center gap-3">
          <OnlineBadge />
          <button
            onClick={() => {
              logout()
              navigate('/login')
            }}
            aria-label="Log out"
            className="text-gas-blue hover:text-white"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">{children}</main>

      <nav className="bg-white border-t border-slate-200 flex justify-around pb-safe">
        {tabs.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-col items-center py-2 px-3 text-xs ${
                isActive ? 'text-gas-navy' : 'text-slate-400'
              }`
            }
          >
            <Icon size={20} />
            <span className="mt-0.5">{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
