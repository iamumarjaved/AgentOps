import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  Play,
  BarChart3,
  ClipboardCheck,
  Shield,
  FlaskConical,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/runs', icon: Play, label: 'Runs' },
  { to: '/metrics', icon: BarChart3, label: 'Metrics' },
  { to: '/evaluations', icon: ClipboardCheck, label: 'Evaluations' },
  { to: '/guardrails', icon: Shield, label: 'Guardrails' },
  { to: '/experiments', icon: FlaskConical, label: 'Experiments' },
]

export default function Layout() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold tracking-tight">AgentOps</h1>
          <p className="text-xs text-gray-400 mt-1">Multi-Agent Observability</p>
        </div>
        <nav className="flex-1 px-3">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm mb-1 transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-xs text-gray-500">v0.1.0</div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
