import { AlertTriangle, CloudRain, Thermometer, Wind, Zap } from 'lucide-react'

const icons = { HEAVY_RAIN: CloudRain, FLOOD: AlertTriangle, HEAT: Thermometer, AQI: Wind, ORDER_SUSPENSION: Zap }

export default function ZoneAlertBanner({ triggers = [] }) {
  if (!triggers.length) {
    return (
      <div className="glass-card p-4 flex items-center gap-3 border border-safety-500/20">
        <div className="w-3 h-3 rounded-full bg-safety-500 animate-pulse" />
        <p className="text-sm text-safety-400 font-medium">All clear — no active disruptions in your zone</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {triggers.map((t, i) => {
        const Icon = icons[t.trigger_type] || AlertTriangle
        const severity = t.severity === 'CRITICAL' ? 'border-danger-500/40 bg-danger-500/5' : 'border-alert-500/40 bg-alert-500/5'
        return (
          <div key={i} className={`glass-card p-4 flex items-center gap-3 border ${severity} animate-slide-in`}>
            <Icon className={`w-5 h-5 ${t.severity === 'CRITICAL' ? 'text-danger-400' : 'text-alert-400'}`} />
            <div className="flex-1">
              <p className="text-sm font-medium text-white">{t.trigger_type.replace(/_/g, ' ')} Alert</p>
              <p className="text-xs text-gray-400">Zone: {t.zone_code} | Sources: {t.sources_agreeing}/3 agree</p>
            </div>
            <span className={t.severity === 'CRITICAL' ? 'badge-red' : 'badge-amber'}>{t.severity}</span>
          </div>
        )
      })}
    </div>
  )
}
