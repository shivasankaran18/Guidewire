import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { Shield, LayoutDashboard, FileText, AlertTriangle, User, LogOut, Settings, Sparkles } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const isActive = (path) => location.pathname === path

  const handleLogout = () => { logout(); navigate('/') }

  const workerLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/assistant', label: 'AI Assistant', icon: Sparkles },
    { path: '/policy', label: 'Coverage', icon: Shield },
    { path: '/claims', label: 'Claims', icon: FileText },
  ]

  const adminLinks = [
    { path: '/admin', label: 'Admin Panel', icon: Settings },
    { path: '/dashboard', label: 'Worker View', icon: LayoutDashboard },
  ]

  const links = user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN' ? adminLinks : workerLinks

  return (
    <nav className="sticky top-0 z-50 bg-[#0f172a]/80 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/dashboard" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-shield-500 to-shield-700 flex items-center justify-center group-hover:shadow-neon-blue transition-shadow">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-display font-bold gradient-text">GigPulse Sentinel</span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {links.map(({ path, label, icon: Icon }) => (
              <Link key={path} to={path} className={isActive(path) ? 'nav-link-active' : 'nav-link'}>
                <span className="flex items-center gap-2">
                  <Icon className="w-4 h-4" />
                  {label}
                </span>
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
              <User className="w-4 h-4 text-shield-400" />
              <span className="text-sm text-gray-300">{user?.name}</span>
              <span className="badge-blue text-[10px]">{user?.role}</span>
            </div>
            <button onClick={handleLogout} className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-all" title="Logout">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
