import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { Shield, LayoutDashboard, FileText, User, LogOut, Settings, Sparkles, Bell } from 'lucide-react'
import { useEffect, useState } from 'react'
import api from '../../utils/api'
import NotificationDrawer from './NotificationDrawer'

export default function Navbar() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [notifOpen, setNotifOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const isActive = (path) => location.pathname === path

  const handleLogout = () => { logout(); navigate('/') }

  const canShowInbox = user?.role !== 'ADMIN' && user?.role !== 'SUPER_ADMIN'

  const loadUnread = async () => {
    try {
      const res = await api.get('/api/workers/notifications/unread-count')
      setUnreadCount(res.data?.unread_count ?? 0)
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    if (!canShowInbox) return
    loadUnread()
    const t = setInterval(loadUnread, 15000)
    return () => clearInterval(t)
  }, [canShowInbox])

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
            {canShowInbox && (
              <>
                <button
                  onClick={() => setNotifOpen(true)}
                  className={
                    `hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl border transition-all ` +
                    (unreadCount > 0
                      ? 'bg-shield-500/15 border-shield-500/40 hover:bg-shield-500/20 shadow-neon-blue'
                      : 'bg-white/5 border-white/10 hover:bg-white/10')
                  }
                  title="Inbox"
                >
                  <span className="relative">
                    <Bell className={unreadCount > 0 ? 'w-4 h-4 text-shield-200' : 'w-4 h-4 text-gray-300'} />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-danger-500 ring-2 ring-[#0f172a]" />
                    )}
                  </span>
                  <span className={unreadCount > 0 ? 'text-sm font-semibold text-shield-100' : 'text-sm text-gray-200'}>
                    Inbox
                  </span>
                  {unreadCount > 0 && (
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-danger-500/20 text-danger-200 border border-danger-500/30">
                      {unreadCount}
                    </span>
                  )}
                </button>

                <button
                  onClick={() => setNotifOpen(true)}
                  className={
                    `sm:hidden p-2.5 rounded-xl border transition-all relative ` +
                    (unreadCount > 0
                      ? 'bg-shield-500/15 border-shield-500/40 shadow-neon-blue'
                      : 'bg-white/5 border-white/10')
                  }
                  title="Inbox"
                >
                  <Bell className={unreadCount > 0 ? 'w-5 h-5 text-shield-200' : 'w-5 h-5 text-gray-300'} />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-danger-500 text-[10px] text-white flex items-center justify-center ring-2 ring-[#0f172a]">
                      {unreadCount}
                    </span>
                  )}
                </button>

                <NotificationDrawer isOpen={notifOpen} onClose={() => { setNotifOpen(false); loadUnread() }} />
              </>
            )}

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
