import { useState, useEffect } from 'react'
import api from '../../utils/api'
import { AlertTriangle, MapPin, Users, Radio, Shield } from 'lucide-react'

export default function FraudRingAlert() {
  const [rings, setRings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/admin/fraud-rings')
      .then(r => setRings(r.data?.live_detection || r.data?.stored_rings || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  // Demo data if empty
  const data = rings.length ? rings : [
    {
      cluster_id: 0, member_count: 7, confidence: 85, severity: 'CRITICAL',
      center_latitude: 12.9815, center_longitude: 80.2180, radius_meters: 87,
      member_ids: ['w-1', 'w-2', 'w-3', 'w-4', 'w-5', 'w-6', 'w-7'],
      home_zones: ['CHN-VEL-4B', 'CHN-ANN-2A', 'BLR-KOR-1A'],
      detection_methods: ['SPATIAL_CLUSTER', 'TIMING_SYNC', 'IP_CORRELATION'],
      timing_spread_seconds: 12.5,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-danger-400" /> Fraud Ring Detection (DBSCAN)
        </h2>
        <span className="badge-red">{data.length} Ring{data.length !== 1 ? 's' : ''} Detected</span>
      </div>

      {data.map((ring, i) => (
        <div key={i} className={`glass-card p-6 border ${ring.severity === 'CRITICAL' ? 'border-danger-500/40' : 'border-alert-500/40'}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-white font-bold text-lg">Ring #{ring.cluster_id + 1}</h3>
              <p className="text-sm text-gray-400 flex items-center gap-1 mt-1">
                <Users className="w-4 h-4" /> {ring.member_count} members •
                <MapPin className="w-4 h-4 ml-1" /> {ring.radius_meters}m radius
              </p>
            </div>
            <div className="text-right">
              <span className={ring.severity === 'CRITICAL' ? 'badge-red' : 'badge-amber'}>{ring.severity}</span>
              <p className="text-xs text-gray-400 mt-1">{ring.confidence}% confidence</p>
            </div>
          </div>

          {/* Detection Methods */}
          <div className="flex flex-wrap gap-2 mb-4">
            {ring.detection_methods?.map((m, j) => (
              <span key={j} className="badge-blue text-xs">{m.replace(/_/g, ' ')}</span>
            ))}
          </div>

          {/* Cluster Insights */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-400">Home Zones</p>
              <p className="text-white font-bold">{ring.home_zones?.length || 0} zones</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-400">Timing Spread</p>
              <p className="text-white font-bold">{ring.timing_spread_seconds?.toFixed(1)}s</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-400">Center</p>
              <p className="text-white font-bold text-xs">{ring.center_latitude?.toFixed(4)}, {ring.center_longitude?.toFixed(4)}</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-xs text-gray-400">Radius</p>
              <p className="text-white font-bold">{ring.radius_meters}m</p>
            </div>
          </div>

          {/* Member IDs */}
          <div className="bg-white/5 rounded-lg p-3">
            <p className="text-xs text-gray-400 mb-2">Member Worker IDs</p>
            <div className="flex flex-wrap gap-1">
              {ring.member_ids?.slice(0, 10).map((id, j) => (
                <span key={j} className="text-xs bg-danger-500/20 text-danger-300 px-2 py-0.5 rounded">{id.slice(0, 8)}...</span>
              ))}
            </div>
          </div>

          <div className="flex gap-3 mt-4">
            <button className="btn-danger flex-1 text-sm py-2">🔒 Freeze Ring Accounts</button>
            <button className="btn-secondary flex-1 text-sm py-2">📋 Export Report</button>
          </div>
        </div>
      ))}
    </div>
  )
}
