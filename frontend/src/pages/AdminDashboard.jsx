import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import FraudRingAlert from '../components/admin/FraudRingAlert'
import LiquidityMeter from '../components/admin/LiquidityMeter'
import LossRatioChart from '../components/admin/LossRatioChart'
import PredictiveRiskMap from '../components/admin/PredictiveRiskMap'
import WorkerTrustTable from '../components/admin/WorkerTrustTable'
import AdminActionLog from '../components/admin/AdminActionLog'
import AdminAIWorkbench from '../components/admin/AdminAIWorkbench'
import { formatCurrency } from '../utils/formatCurrency'
import api from '../utils/api'
import { Users, FileText, AlertTriangle, IndianRupee, Shield, Clock, TrendingUp, Eye, Sparkles } from 'lucide-react'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [reviewQueue, setReviewQueue] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('overview')

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const [dashRes, reviewRes] = await Promise.allSettled([
        api.get('/api/admin/dashboard'),
        api.get('/api/admin/claims/review'),
      ])
      if (dashRes.status === 'fulfilled') setDashboard(dashRes.value.data)
      if (reviewRes.status === 'fulfilled') setReviewQueue(reviewRes.value.data?.claims || [])
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const handleResolve = async (claimId, action, notes = '') => {
    try {
      await api.post(`/api/admin/claims/${claimId}/resolve`, { action, notes })
      await loadData()
    } catch (e) { alert(e.response?.data?.detail || 'Failed') }
  }

  if (loading) return <LoadingSpinner text="Loading admin panel..." />

  const d = dashboard || {
    total_workers: 52, active_policies: 38, total_claims_today: 12,
    pending_review_count: 3, total_payouts_today: 8450, active_triggers: 4,
    fraud_rings_detected: 1,
    risk_distribution: { GREEN: 42, AMBER: 7, RED: 3 },
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'ai', label: 'AI Workbench', icon: Sparkles },
    { id: 'review', label: `Review Queue (${d.pending_review_count})`, icon: Eye },
    { id: 'fraud', label: 'Fraud Rings', icon: AlertTriangle },
    { id: 'workers', label: 'Workers', icon: Users },
    { id: 'logs', label: 'Audit Log', icon: FileText },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 animate-slide-in">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Admin Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Logged in as <span className="text-shield-400">{user?.name}</span></p>
        </div>
        <span className="badge-blue mt-2 sm:mt-0">{user?.role}</span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2 animate-slide-in">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${
              tab === t.id ? 'bg-shield-600/30 text-white border border-shield-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
            <t.icon className="w-4 h-4" />{t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {tab === 'overview' && (
        <div className="space-y-8">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
            {[
              { icon: Users, label: 'Total Workers', value: d.total_workers, color: 'text-white' },
              { icon: Shield, label: 'Active Policies', value: d.active_policies, color: 'text-shield-400' },
              { icon: Clock, label: 'Pending Review', value: d.pending_review_count, color: 'text-alert-400' },
              { icon: IndianRupee, label: 'Paid Today', value: formatCurrency(d.total_payouts_today), color: 'text-safety-400' },
            ].map(({ icon: Icon, label, value, color }) => (
              <div key={label} className="stat-card">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                    <Icon className={`w-5 h-5 ${color}`} />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">{label}</p>
                    <p className={`text-2xl font-bold ${color}`}>{value}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Risk Distribution */}
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-sm font-semibold text-gray-400 uppercase mb-4">Risk Distribution</h3>
              <div className="space-y-3">
                {Object.entries(d.risk_distribution || {}).map(([tier, count]) => {
                  const total = Object.values(d.risk_distribution).reduce((a, b) => a + b, 0)
                  const pct = total > 0 ? (count / total * 100) : 0
                  const colors = { GREEN: 'bg-safety-500', AMBER: 'bg-alert-500', RED: 'bg-danger-500' }
                  const labels = { GREEN: '🟢 Green', AMBER: '🟡 Amber', RED: '🔴 Red' }
                  return (
                    <div key={tier}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">{labels[tier]}</span>
                        <span className="text-white font-medium">{count} ({pct.toFixed(0)}%)</span>
                      </div>
                      <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${colors[tier]}`} style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
            <LiquidityMeter premiumsCollected={15200} claimsPaid={d.total_payouts_today || 8450} />
            <LossRatioChart />
          </div>

          <PredictiveRiskMap />
        </div>
      )}

      {tab === 'ai' && <AdminAIWorkbench />}

      {/* Review Queue Tab */}
      {tab === 'review' && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white">Claims Pending Review</h2>
          {(reviewQueue.length ? reviewQueue : [
            { id: 'rev-1', claim_type: 'HEAVY_RAIN', zone_code: 'CHN-VEL-4B', fraud_tier: 'AMBER', fraud_score: 48, calculated_payout: 920, status: 'PENDING', confidence_score: 52 },
            { id: 'rev-2', claim_type: 'AQI', zone_code: 'DEL-CON-1A', fraud_tier: 'RED', fraud_score: 72, calculated_payout: 1350, status: 'PENDING', confidence_score: 28 },
            { id: 'rev-3', claim_type: 'FLOOD', zone_code: 'MUM-AND-1A', fraud_tier: 'AMBER', fraud_score: 35, calculated_payout: 780, status: 'APPEALED', confidence_score: 65 },
          ]).map(claim => (
            <div key={claim.id} className="glass-card p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-white font-semibold">{claim.claim_type?.replace(/_/g, ' ')}</p>
                  <p className="text-xs text-gray-400">Zone: {claim.zone_code} | Fraud Score: {claim.fraud_score}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-white">{formatCurrency(claim.calculated_payout)}</p>
                  <span className={claim.fraud_tier === 'RED' ? 'badge-red' : 'badge-amber'}>{claim.fraud_tier}</span>
                </div>
              </div>
              <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden mb-4">
                <div className={`h-full rounded-full ${claim.fraud_tier === 'RED' ? 'bg-danger-500' : 'bg-alert-500'}`}
                     style={{ width: `${claim.confidence_score || 50}%` }} />
              </div>
              <div className="flex gap-3">
                <button onClick={() => handleResolve(claim.id, 'APPROVE', 'Admin approved after review')} className="btn-success flex-1 text-sm py-2">✓ Approve & Pay</button>
                <button onClick={() => handleResolve(claim.id, 'REJECT', 'Fraud indicators confirmed')} className="btn-danger flex-1 text-sm py-2">✗ Reject</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'fraud' && <FraudRingAlert />}
      {tab === 'workers' && <WorkerTrustTable />}
      {tab === 'logs' && <AdminActionLog />}
    </div>
  )
}
