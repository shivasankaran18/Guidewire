import { BarChart3 } from 'lucide-react'

const weeklyData = [
  { week: 'W09', premiums: 12500, claims: 5200, ratio: 0.42 },
  { week: 'W10', premiums: 14200, claims: 8900, ratio: 0.63 },
  { week: 'W11', premiums: 13800, claims: 3100, ratio: 0.22 },
  { week: 'W12', premiums: 15200, claims: 8450, ratio: 0.56 },
  { week: 'W13', premiums: 16100, claims: 11200, ratio: 0.70 },
]

export default function LossRatioChart() {
  const maxPremium = Math.max(...weeklyData.map(d => d.premiums))
  const avgRatio = (weeklyData.reduce((s, d) => s + d.ratio, 0) / weeklyData.length * 100).toFixed(0)

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-shield-400" />
          <h3 className="text-sm font-semibold text-gray-400 uppercase">Loss Ratio</h3>
        </div>
        <span className="text-xs text-gray-400">Avg: {avgRatio}%</span>
      </div>

      <div className="space-y-3">
        {weeklyData.map(d => (
          <div key={d.week}>
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>{d.week}</span>
              <span className={d.ratio > 0.6 ? 'text-alert-400' : 'text-safety-400'}>
                {(d.ratio * 100).toFixed(0)}%
              </span>
            </div>
            <div className="relative w-full h-4 bg-white/5 rounded-full overflow-hidden">
              <div className="absolute h-full bg-shield-500/40 rounded-full" style={{ width: `${(d.premiums / maxPremium) * 100}%` }} />
              <div className={`absolute h-full rounded-full ${d.ratio > 0.6 ? 'bg-alert-500/60' : 'bg-safety-500/60'}`}
                   style={{ width: `${(d.claims / maxPremium) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-4 mt-4 text-xs text-gray-400">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-shield-500/40" /> Premiums</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-safety-500/60" /> Claims</span>
      </div>
    </div>
  )
}
