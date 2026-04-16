import { useState, useEffect } from 'react'
import api from '../../utils/api'
import { ScrollText, Shield, AlertTriangle, CheckCircle, XCircle, ShieldCheck, History } from 'lucide-react'

export default function AdminActionLog() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [verified, setVerified] = useState(null)
  const [entityFilter, setEntityFilter] = useState('ALL')

  useEffect(() => {
    loadLogs()
    verifyChain()
  }, [])

  const loadLogs = async () => {
    try {
      const res = await api.get('/api/admin/audit-log?limit=50')
      setLogs(res.data.entries || res.data.demo_entries || [])
    } catch (e) {
      console.error('Failed to load audit log', e)
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  const verifyChain = async () => {
    try {
      const res = await api.get('/api/admin/audit-log/verify')
      setVerified(res.data)
    } catch (e) {
      setVerified({ valid: false, message: 'Verification failed' })
    }
  }

  const getIcon = (action) => {
    if (action.includes('APPROVED') || action.includes('APPROVE')) return { icon: CheckCircle, color: 'text-safety-400' }
    if (action.includes('REJECTED') || action.includes('REJECT')) return { icon: XCircle, color: 'text-danger-400' }
    if (action.includes('TRIGGER')) return { icon: AlertTriangle, color: 'text-alert-400' }
    if (action.includes('FRAUD')) return { icon: ShieldCheck, color: 'text-danger-400' }
    if (action.includes('POLICY')) return { icon: Shield, color: 'text-shield-400' }
    return { icon: History, color: 'text-gray-400' }
  }

  const formatTime = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    const now = new Date()
    const diff = Math.floor((now - date) / 60000)
    if (diff < 1) return 'Just now'
    if (diff < 60) return `${diff} min ago`
    if (diff < 1440) return `${Math.floor(diff / 60)} hr ago`
    return date.toLocaleDateString()
  }

  const filteredLogs = entityFilter === 'ALL' ? logs : logs.filter(l => l.entity_type === entityFilter)
  const entityTypes = ['ALL', ...new Set(logs.map(l => l.entity_type).filter(Boolean))]

  if (loading) {
    return (
      <div className="glass-card p-8 text-center">
        <div className="animate-spin w-8 h-8 border-2 border-shield-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-400">Loading audit logs...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Verification Status */}
      <div className="glass-card p-4 border border-shield-500/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {verified?.valid ? (
              <CheckCircle className="w-5 h-5 text-safety-400" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-alert-400" />
            )}
            <div>
              <p className="text-white font-medium">SHA-256 Hash Chain</p>
              <p className="text-gray-400 text-sm">{verified?.message || 'Verifying...'}</p>
            </div>
          </div>
          <div className="text-right text-sm">
            <p className="text-gray-400">Entries Checked</p>
            <p className="text-white font-medium">{verified?.entries_checked || 0}</p>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <FilterIcon className="w-4 h-4 text-gray-400" />
        {entityTypes.map(et => (
          <button key={et} onClick={() => setEntityFilter(et)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              entityFilter === et ? 'bg-shield-600/30 text-white border border-shield-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}>
            {et}
          </button>
        ))}
      </div>

      {/* Logs */}
      {filteredLogs.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <ScrollText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">No audit logs found.</p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <div className="divide-y divide-white/5 max-h-[500px] overflow-y-auto">
            {filteredLogs.map((log, i) => {
              const { icon: Icon, color } = getIcon(log.action)
              return (
                <div key={log.id || i} className="flex items-start gap-4 p-4 hover:bg-white/5 transition-colors">
                  <div className={`w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0 mt-0.5`}>
                    <Icon className={`w-4 h-4 ${color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-sm font-semibold text-white">{log.action.replace(/_/g, ' ')}</span>
                      <span className="badge-blue text-[9px]">{log.entity_type}</span>
                    </div>
                    <p className="text-sm text-gray-400">
                      {log.new_state ? Object.entries(log.new_state).map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`).join(', ') : 'No details'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      By: {log.actor_id || 'system'}{log.actor_role ? ` (${log.actor_role})` : ''} • {formatTime(log.created_at)}
                    </p>
                  </div>
                  <div className="text-[10px] text-gray-600 font-mono mt-1 shrink-0">
                    #{String(log.id || i).slice(-6)}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <p className="text-xs text-gray-500 text-center">
        🔒 All entries are immutable and verified via SHA-256 hash chain. Tampering is detectable.
      </p>
    </div>
  )
}

function FilterIcon({ className }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
    </svg>
  )
}