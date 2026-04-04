import { formatCurrency } from '../../utils/formatCurrency'
import { Shield, CheckCircle } from 'lucide-react'

export default function CoverageCard({ policy }) {
  if (!policy) {
    return (
      <div className="glass-card p-6 border-dashed border-2 border-white/10">
        <div className="text-center py-4">
          <Shield className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 font-medium">No Active Coverage</p>
          <p className="text-xs text-gray-500 mt-1">Activate a plan to get protected</p>
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card p-6 border border-shield-500/30 animate-pulse-glow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider">Active Coverage</p>
          <p className="text-2xl font-bold text-white mt-1">{policy.plan_tier} Shield</p>
        </div>
        <div className="w-10 h-10 rounded-xl bg-safety-500/20 flex items-center justify-center">
          <CheckCircle className="w-5 h-5 text-safety-400" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div>
          <p className="text-xs text-gray-400">Premium Paid</p>
          <p className="text-lg font-bold text-white">{formatCurrency(policy.premium_amount)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Max Coverage</p>
          <p className="text-lg font-bold gradient-text-safety">{formatCurrency(policy.coverage_amount)}</p>
        </div>
      </div>
      <div className="mt-4 pt-4 border-t border-white/10 flex justify-between text-xs text-gray-400">
        <span>{policy.week_start?.slice(0, 10)} → {policy.week_end?.slice(0, 10)}</span>
        <span className="badge-green">ACTIVE</span>
      </div>
    </div>
  )
}
