import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { usePremium } from '../hooks/usePremium'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ConfirmModal from '../components/shared/ConfirmModal'
import { formatCurrency } from '../utils/formatCurrency'
import { Shield, CheckCircle, Star, Zap, ArrowRight, Clock, AlertTriangle } from 'lucide-react'

const tierIcons = { BASIC: Shield, STANDARD: Star, PREMIUM: Zap }
const tierColors = {
  BASIC: 'from-gray-500/20 to-gray-600/20 border-gray-500/30 hover:border-gray-400/50',
  STANDARD: 'from-shield-500/20 to-shield-600/20 border-shield-500/30 hover:border-shield-400/50',
  PREMIUM: 'from-amber-500/20 to-orange-600/20 border-amber-500/30 hover:border-amber-400/50',
}
const tierGlow = { BASIC: '', STANDARD: 'shadow-neon-blue', PREMIUM: 'shadow-[0_0_20px_rgba(251,191,36,0.25)]' }

export default function PolicyPage() {
  const { plans, currentPolicy, hasActive, loading, activate } = usePremium()
  const [selected, setSelected] = useState('STANDARD')
  const [showConfirm, setShowConfirm] = useState(false)
  const [activating, setActivating] = useState(false)
  const [history, setHistory] = useState([])

  useEffect(() => {
    import('../utils/api').then(({ default: api }) =>
      api.get('/api/policies/history').then(r => setHistory(r.data)).catch(() => {})
    )
  }, [])

  const handleActivate = async () => {
    setActivating(true)
    try {
      await activate(selected)
      setShowConfirm(false)
    } catch (e) {
      alert(e.response?.data?.detail || 'Activation failed')
    } finally { setActivating(false) }
  }

  if (loading) return <LoadingSpinner text="Loading plans..." />

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 animate-slide-in">
        <h1 className="text-2xl font-display font-bold text-white">Weekly Coverage Plans</h1>
        <p className="text-gray-400 mt-1">AI-priced based on your zone risk. Pay weekly, get protected instantly.</p>
      </div>

      {/* Active Policy Banner */}
      {hasActive && currentPolicy && (
        <div className="glass-card p-6 mb-8 border border-safety-500/30 animate-slide-in">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle className="w-6 h-6 text-safety-400" />
            <h2 className="text-lg font-semibold text-white">Active Coverage This Week</h2>
          </div>
          <div className="grid sm:grid-cols-4 gap-4">
            <div><p className="text-xs text-gray-400">Plan</p><p className="text-white font-bold">{currentPolicy.plan_tier} Shield</p></div>
            <div><p className="text-xs text-gray-400">Premium</p><p className="text-white font-bold">{formatCurrency(currentPolicy.premium_amount)}</p></div>
            <div><p className="text-xs text-gray-400">Max Coverage</p><p className="text-safety-400 font-bold">{formatCurrency(currentPolicy.coverage_amount)}</p></div>
            <div><p className="text-xs text-gray-400">Expires</p><p className="text-white font-bold">{currentPolicy.week_end?.slice(0, 10)}</p></div>
          </div>
        </div>
      )}

      {/* Plan Tiers */}
      <div className="grid md:grid-cols-3 gap-6 mb-12 stagger-children">
        {(plans.length ? plans : [
          { tier: 'BASIC', name: 'Basic Shield', premium_range: '₹29–45', coverage_multiplier: 1.0, description: 'Essential income protection', features: ['Heavy rainfall & flood coverage', 'Payout within 2 hours', 'Up to 1x weekly earnings'] },
          { tier: 'STANDARD', name: 'Standard Shield', premium_range: '₹41–63', coverage_multiplier: 1.5, description: 'Enhanced protection with faster payouts', features: ['All Basic features', 'Heat & AQI coverage', 'Instant Green-tier payout', 'Up to 1.5x weekly earnings'] },
          { tier: 'PREMIUM', name: 'Premium Shield', premium_range: '₹52–75', coverage_multiplier: 2.0, description: 'Maximum protection', features: ['All Standard features', 'Platform suspension coverage', 'Instant Green & Amber payout', 'Up to 2x weekly earnings', '₹50 false positive goodwill'] },
        ]).map((plan) => {
          const Icon = tierIcons[plan.tier] || Shield
          const isSelected = selected === plan.tier
          return (
            <div
              key={plan.tier}
              onClick={() => !hasActive && setSelected(plan.tier)}
              className={`relative glass-card p-6 cursor-pointer transition-all duration-300 border bg-gradient-to-b ${tierColors[plan.tier]}
                ${isSelected ? `scale-[1.03] ${tierGlow[plan.tier]}` : 'hover:scale-[1.01]'}
                ${hasActive ? 'opacity-60 cursor-default' : ''}`}
            >
              {plan.tier === 'STANDARD' && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-shield-500 text-white text-xs font-bold">
                  RECOMMENDED
                </div>
              )}
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${isSelected ? 'bg-white/20' : 'bg-white/10'}`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">{plan.name}</h3>
                  <p className="text-xs text-gray-400">{plan.description}</p>
                </div>
              </div>
              <p className="text-3xl font-display font-extrabold text-white mb-1">{plan.premium_range}</p>
              <p className="text-xs text-gray-400 mb-5">per week • {plan.coverage_multiplier}x coverage</p>
              <ul className="space-y-2">
                {plan.features?.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <CheckCircle className="w-4 h-4 text-safety-400 mt-0.5 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              {isSelected && !hasActive && (
                <button onClick={(e) => { e.stopPropagation(); setShowConfirm(true) }} className="btn-primary w-full mt-6 flex items-center justify-center gap-2">
                  Activate {plan.name} <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          )
        })}
      </div>

      {/* Past Policies */}
      {history.length > 0 && (
        <div className="animate-slide-in">
          <h2 className="text-lg font-display font-bold text-white mb-4 flex items-center gap-2"><Clock className="w-5 h-5 text-gray-400" /> Policy History</h2>
          <div className="glass-card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-gray-400 text-xs uppercase">
                  <th className="px-4 py-3 text-left">Plan</th>
                  <th className="px-4 py-3 text-left">Premium</th>
                  <th className="px-4 py-3 text-left">Coverage</th>
                  <th className="px-4 py-3 text-left">Period</th>
                  <th className="px-4 py-3 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((p) => (
                  <tr key={p.id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="px-4 py-3 text-white font-medium">{p.plan_tier}</td>
                    <td className="px-4 py-3 text-white">{formatCurrency(p.premium_amount)}</td>
                    <td className="px-4 py-3 text-safety-400">{formatCurrency(p.coverage_amount)}</td>
                    <td className="px-4 py-3 text-gray-400">{p.week_start?.slice(0, 10)}</td>
                    <td className="px-4 py-3"><span className={p.status === 'ACTIVE' ? 'badge-green' : 'badge-blue'}>{p.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={showConfirm}
        title="Activate Coverage?"
        message={`You're about to activate ${selected} Shield coverage for this week. Premium will be deducted via UPI.`}
        confirmText={activating ? 'Activating...' : 'Confirm & Pay'}
        onConfirm={handleActivate}
        onCancel={() => setShowConfirm(false)}
      />
    </div>
  )
}
