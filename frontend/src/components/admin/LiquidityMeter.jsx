import { formatCurrency } from '../../utils/formatCurrency'
import { Wallet } from 'lucide-react'

export default function LiquidityMeter({ premiumsCollected = 15200, claimsPaid = 8450 }) {
  const balance = premiumsCollected - claimsPaid
  const ratio = premiumsCollected > 0 ? balance / premiumsCollected : 0
  const pct = Math.max(0, Math.min(100, ratio * 100))

  let color, status
  if (ratio >= 0.4) { color = 'text-safety-400'; status = '🟢 Healthy' }
  else if (ratio >= 0.2) { color = 'text-alert-400'; status = '🟡 Watch' }
  else { color = 'text-danger-400'; status = '🔴 Critical' }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Wallet className="w-5 h-5 text-shield-400" />
        <h3 className="text-sm font-semibold text-gray-400 uppercase">Liquidity Pool</h3>
      </div>

      <div className="text-center mb-4">
        <p className={`text-3xl font-display font-extrabold ${color}`}>{formatCurrency(balance)}</p>
        <p className="text-xs text-gray-400 mt-1">{status}</p>
      </div>

      <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden mb-4">
        <div className={`h-full rounded-full transition-all duration-1000 ${ratio >= 0.4 ? 'bg-safety-500' : ratio >= 0.2 ? 'bg-alert-500' : 'bg-danger-500'}`}
             style={{ width: `${pct}%` }} />
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-400">Premiums In</p>
          <p className="text-safety-400 font-bold">{formatCurrency(premiumsCollected)}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-400">Claims Out</p>
          <p className="text-danger-400 font-bold">{formatCurrency(claimsPaid)}</p>
        </div>
      </div>
    </div>
  )
}
