import { useEffect, useState } from 'react'
import api from '../../utils/api'
import { X, Bell, Check } from 'lucide-react'

function typeDot(type) {
  if (type === 'PAYOUT') return 'bg-safety-500'
  if (type === 'WARNING') return 'bg-danger-500'
  if (type === 'ALERT') return 'bg-alert-500'
  if (type === 'COVERAGE') return 'bg-shield-500'
  return 'bg-white/40'
}

export default function NotificationDrawer({ isOpen, onClose }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get('/api/workers/notifications?limit=20')
      setItems(res.data?.notifications || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) load()
  }, [isOpen])

  const unreadCount = items.filter(n => !n.read_at).length

  const markAllRead = async () => {
    try {
      await api.post('/api/workers/notifications/read-all')
      setItems(prev => prev.map(n => ({ ...n, read_at: n.read_at || new Date().toISOString() })))
    } catch (e) { alert(e.response?.data?.detail || 'Failed') }
  }

  const markRead = async (id) => {
    try {
      await api.post(`/api/workers/notifications/${id}/read`)
      setItems(prev => prev.map(n => n.id === id ? { ...n, read_at: n.read_at || new Date().toISOString() } : n))
    } catch (e) { /* ignore */ }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[60]">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      <div className="absolute right-0 top-0 h-full w-full sm:w-[420px] bg-[#0b1224] border-l border-white/10 shadow-2xl">
        <div className="h-16 px-4 flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-gray-300" />
            <div>
              <div className="text-white font-semibold leading-5">Notifications</div>
              <div className="text-xs text-gray-400">{unreadCount} unread</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={markAllRead} className="text-xs px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 flex items-center gap-1">
              <Check className="w-3.5 h-3.5" /> Mark all read
            </button>
            <button onClick={onClose} className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10" title="Close">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-4 overflow-auto h-[calc(100%-4rem)]">
          {loading && <div className="text-sm text-gray-400">Loading…</div>}
          {!loading && items.length === 0 && (
            <div className="glass-card p-4 text-sm text-gray-400">No notifications yet.</div>
          )}

          <div className="space-y-3">
            {items.map(n => (
              <button
                key={n.id}
                onClick={() => markRead(n.id)}
                className={`w-full text-left glass-card p-4 border ${n.read_at ? 'border-white/10' : 'border-shield-500/30'} hover:bg-white/5 transition-colors`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${typeDot(n.type)}`} />
                      <div className="text-white font-semibold truncate">{n.title}</div>
                    </div>
                    <div className="text-sm text-gray-300 mt-1">{n.message}</div>
                    {n.data?.claim_id && (
                      <div className="text-xs text-gray-500 mt-2">Claim: {n.data.claim_id}</div>
                    )}
                  </div>
                  {!n.read_at && <span className="text-[10px] px-2 py-1 rounded-full bg-shield-500/20 text-shield-200 border border-shield-500/30">NEW</span>}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
