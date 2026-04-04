export default function PoolHealthIndicator({ ratio = 0.65 }) {
  const pct = Math.round(ratio * 100)
  let color, icon, label

  if (ratio >= 0.7) { color = 'text-safety-400'; icon = '🟢'; label = 'Healthy' }
  else if (ratio >= 0.4) { color = 'text-alert-400'; icon = '🟡'; label = 'Moderate' }
  else { color = 'text-danger-400'; icon = '🔴'; label = 'Critical' }

  return (
    <div className="glass-card p-6">
      <p className="text-xs text-gray-400 uppercase tracking-wider mb-3">Liquidity Pool</p>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div className="flex-1">
          <p className={`text-lg font-bold ${color}`}>{pct}% {label}</p>
          <div className="w-full h-2 bg-white/10 rounded-full mt-2 overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-1000 ${ratio >= 0.7 ? 'bg-safety-500' : ratio >= 0.4 ? 'bg-alert-500' : 'bg-danger-500'}`} style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>
    </div>
  )
}
