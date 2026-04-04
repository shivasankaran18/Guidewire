import { MapPin } from 'lucide-react'
import { getAllZones } from '../../utils/zonePolygon'

export default function ZoneSelector({ value, onChange }) {
  const zones = getAllZones()
  const cities = [...new Set(zones.map(z => z.city))]
  const selected = zones.find(z => z.code === value)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <MapPin className="w-5 h-5 text-shield-400" />
        <h3 className="text-sm font-semibold text-white">Select Delivery Zone</h3>
      </div>
      <p className="text-xs text-gray-400">500m polygon precision. Your zone affects your premium pricing.</p>

      <select value={value || ''} onChange={e => onChange?.(e.target.value)} className="input-field">
        <option value="">Select your zone...</option>
        {cities.map(city => (
          <optgroup key={city} label={city}>
            {zones.filter(z => z.city === city).map(z => (
              <option key={z.code} value={z.code}>{z.area} ({z.code})</option>
            ))}
          </optgroup>
        ))}
      </select>

      {selected && (
        <div className="glass-card p-4 animate-slide-in">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-shield-500/20 flex items-center justify-center">
              <MapPin className="w-5 h-5 text-shield-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{selected.area}, {selected.city}</p>
              <p className="text-xs text-gray-400">
                Zone: {selected.code} • Lat: {selected.lat.toFixed(4)} • Lng: {selected.lng.toFixed(4)}
              </p>
            </div>
          </div>

          {/* Simulated zone polygon outline */}
          <div className="mt-4 h-32 bg-white/5 rounded-xl border border-white/10 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto border-2 border-dashed border-shield-500/50 rounded-lg flex items-center justify-center rotate-12">
                <div className="w-8 h-8 bg-shield-500/20 rounded" />
              </div>
              <p className="text-[10px] text-gray-500 mt-2">Sub-zone polygon (500m)</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
