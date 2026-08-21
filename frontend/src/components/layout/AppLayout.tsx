import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Car,
  LayoutDashboard,
  LogOut,
  Video,
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

const navigation = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/cameras', label: 'Caméras', icon: Video },
  { to: '/trafic', label: 'Trafic', icon: Activity },
  { to: '/incidents', label: 'Incidents', icon: AlertTriangle },
  { to: '/vehicules', label: 'Véhicules', icon: Car },
  { to: '/analytique', label: 'Analytique', icon: BarChart3 },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex">
      <aside className="w-56 shrink-0 border-r border-gray-800 bg-gray-900/50 flex flex-col">
        <div className="h-16 flex items-center gap-2 px-5 border-b border-gray-800">
          <div className="h-8 w-8 rounded-lg bg-emerald-500 flex items-center justify-center">
            <Activity className="h-5 w-5 text-gray-950" />
          </div>
          <span className="font-bold tracking-tight">UrbanTraffic</span>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navigation.map(({ to, label, icon: Icon, ...rest }) => (
            <NavLink
              key={to}
              to={to}
              end={'end' in rest ? rest.end : false}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 shrink-0 border-b border-gray-800 bg-gray-900/50 flex items-center justify-between px-6">
          <p className="text-sm text-gray-400">
            Système intelligent de gestion du trafic urbain — Kinshasa
          </p>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user?.username}</p>
              <p className="text-xs text-emerald-400 uppercase">{user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Se déconnecter"
              className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
