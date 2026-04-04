import { MapPin } from 'lucide-react'

const zones = [
  { code: 'CHN-VEL-4B', city: 'Chennai', area: 'Velachery', risk: 85, nextWeek: 'HIGH', triggers: ['HEAVY_RAIN', 'FLOOD'] },
  { code: 'MUM-AND-1A', city: 'Mumbai', area: 'Andheri', risk: 78, nextWeek: 'HIGH', triggers: ['HEAVY_RAIN'] },
  { code: 'DEL-CON-1A', city: 'Delhi', area: 'Connaught Place', risk: 72, nextWeek: 'HIGH', triggers: ['AQI', 'HEAT'] },
  { code: 'MUM-DAD-3A', city: 'Mumbai', area: 'Dadar', risk: 70, nextWeek: 'MEDIUM', triggers: ['HEAVY_RAIN'] },
  { code: 'CHN-SHN-6A', city: 'Chennai', area: 'Sholinganallur', risk: 68, nextWeek: 'MEDIUM', triggers: ['FLOOD'] },
  { code: 'BLR-KOR-1A', city: 'Bengaluru', area: 'Koramangala', risk: 52, nextWeek: 'MEDIUM', triggers: ['HEAVY_RAIN'] },
  { code: 'HYD-HIB-1A', city: 'Hyderabad', area: 'HITEC City', risk: 35, nextWeek: 'LOW', triggers: [] },
  { code: 'BLR-IND-2A', city: 'Bengaluru', area: 'Indiranagar', risk: 28, nextWeek: 'LOW', triggers: [] },
]

export default function PredictiveRiskMap() {
  const riskColor = (risk) => {
    if (risk >= 70) return 'bg-danger-500'
    if (risk >= 50) return 'bg-alert-500'
    return 'bg-safety-500'
  }

  const riskText = (level) => {
    if (level === 'HIGH') return 'text-danger-400'
    if (level === 'MEDIUM') return 'text-alert-400'
    return 'text-safety-400'
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-shield-400" />
          <h3 className="text-lg font-bold text-white">Predictive Zone Risk Heatmap</h3>
        </div>
        <span className="text-xs text-gray-400">Next Week Forecast</span>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3">
        {zones.map(z => (
          <div key={z.code} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-semibold text-white">{z.area}</p>
              <div className={`w-3 h-3 rounded-full ${riskColor(z.risk)}`} />
            </div>
            <p className="text-xs text-gray-400">{z.city} • {z.code}</p>
            <div className="flex items-center justify-between mt-3">
              <div className="w-full mr-3">
                <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${riskColor(z.risk)}`} style={{ width: `${z.risk}%` }} />
                </div>
              </div>
              <span className={`text-xs font-bold ${riskText(z.nextWeek)}`}>{z.risk}%</span>
            </div>
            {z.triggers.length > 0 && (
              <div className="flex gap-1 mt-2">
                {z.triggers.map((t, i) => (
                  <span key={i} className="text-[10px] bg-white/10 text-gray-300 px-1.5 py-0.5 rounded">{t}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-4 mt-4 text-xs text-gray-400">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-danger-500" /> High Risk (70%+)</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-alert-500" /> Medium (50–70%)</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-safety-500" /> Low (&lt;50%)</span>
      </div>
    </div>
  )
}
