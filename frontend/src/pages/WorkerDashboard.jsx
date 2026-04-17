import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import CoverageCard from '../components/dashboard/CoverageCard'
import EarningsProtected from '../components/dashboard/EarningsProtected'
import TrustScoreBadge from '../components/dashboard/TrustScoreBadge'
import ZoneAlertBanner from '../components/dashboard/ZoneAlertBanner'
import WeeklyReceipt from '../components/dashboard/WeeklyReceipt'
import PoolHealthIndicator from '../components/dashboard/PoolHealthIndicator'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import NotificationDrawer from '../components/shared/NotificationDrawer'
import api from '../utils/api'
import { formatCurrency } from '../utils/formatCurrency'
import { Shield, Bell, Clock, MapPin } from 'lucide-react'

export default function WorkerDashboard() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [policy, setPolicy] = useState(null)
  const [triggers, setTriggers] = useState([])
  const [trustScore, setTrustScore] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notifOpen, setNotifOpen] = useState(false)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      const [profileRes, policyRes, triggerRes, trustRes] = await Promise.allSettled([
        api.get('/api/workers/profile'),
        api.get('/api/policies/current'),
        api.get('/api/triggers/status'),
        api.get('/api/workers/trust-score'),
      ])
      if (profileRes.status === 'fulfilled') setProfile(profileRes.value.data)
      if (policyRes.status === 'fulfilled') setPolicy(policyRes.value.data)
      if (triggerRes.status === 'fulfilled') setTriggers(triggerRes.value.data?.active_triggers || [])
      if (trustRes.status === 'fulfilled') setTrustScore(trustRes.value.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  if (loading) return <LoadingSpinner text="Loading dashboard..." />

  // Use profile data or demo defaults
  const p = profile || { name: user?.name, primary_zone_code: 'CHN-VEL-4B', avg_weekly_earnings: 4200, trust_score: 78.5, fraud_strikes: 0 }
  const activePolicy = policy?.has_active_policy ? policy.policy : null

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 animate-slide-in">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">
            Welcome back, <span className="gradient-text">{p.name?.split(' ')[0] || 'Worker'}</span> 👋
          </h1>
          <div className="flex items-center gap-3 mt-2 text-sm text-gray-400">
            <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {p.primary_zone_code}</span>
            <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Week of Apr 1–7</span>
          </div>
        </div>
        <button
          onClick={() => setNotifOpen(true)}
          className="mt-3 sm:mt-0 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
          title="Inbox"
        >
          <Bell className="w-5 h-5 text-gray-300" />
          <span className="text-sm text-gray-200 hidden sm:inline">Inbox</span>
        </button>
      </div>

      <NotificationDrawer isOpen={notifOpen} onClose={() => setNotifOpen(false)} />

      {/* Zone Alerts */}
      <div className="mb-6 animate-slide-in" style={{ animationDelay: '0.05s' }}>
        <ZoneAlertBanner triggers={triggers} />
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-6 stagger-children">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <CoverageCard policy={activePolicy} />
          
          <div className="grid sm:grid-cols-2 gap-6">
            <EarningsProtected weeklyEarnings={p.avg_weekly_earnings} coverageMultiplier={activePolicy?.coverage_multiplier || 1.5} />
            <WeeklyReceipt premiumPaid={activePolicy?.premium_amount || 0} claimsPaid={2} totalPayout={1200} />
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Weekly Earnings', value: formatCurrency(p.avg_weekly_earnings), color: 'text-white' },
              { label: 'Tenure', value: `${p.tenure_weeks || 0} weeks`, color: 'text-shield-400' },
              { label: 'Claims Filed', value: '3', color: 'text-alert-400' },
              { label: 'Total Received', value: '₹3,600', color: 'text-safety-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="stat-card">
                <p className="text-xs text-gray-400">{label}</p>
                <p className={`text-xl font-bold ${color} mt-1`}>{value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <TrustScoreBadge score={trustScore?.trust_score ?? p.trust_score} strikes={trustScore?.fraud_strikes ?? p.fraud_strikes} />
          <PoolHealthIndicator ratio={0.72} />

          {/* Coverage Nudge */}
          {!activePolicy && (
            <div className="glass-card p-6 border border-shield-500/30">
              <Shield className="w-8 h-8 text-shield-400 mb-3" />
              <h3 className="text-white font-semibold mb-2">Get Protected This Week</h3>
              <p className="text-sm text-gray-400 mb-4">Monsoon season is here. Heavy rain expected in your zone.</p>
              <a href="/policy" className="btn-primary w-full text-center block">Activate Coverage →</a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
