import { formatCurrency } from '../../utils/formatCurrency'
import { TrendingUp } from 'lucide-react'

export default function EarningsProtected({ weeklyEarnings = 4200, coverageMultiplier = 1.5 }) {
  const maxProtection = weeklyEarnings * coverageMultiplier

  return (
    <div className="glass-card p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider">Earnings Protected</p>
          <p className="text-2xl font-bold gradient-text-safety mt-1">{formatCurrency(maxProtection)}</p>
        </div>
        <div className="w-10 h-10 rounded-xl bg-safety-500/20 flex items-center justify-center">
          <TrendingUp className="w-5 h-5 text-safety-400" />
        </div>
      </div>
      <div className="mt-2">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Weekly avg: {formatCurrency(weeklyEarnings)}</span>
          <span>{coverageMultiplier}x coverage</span>
        </div>
        <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-safety-500 to-safety-400 rounded-full" style={{ width: `${Math.min(100, coverageMultiplier * 50)}%` }} />
        </div>
      </div>
    </div>
  )
}
