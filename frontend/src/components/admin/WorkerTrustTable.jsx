import { useState, useEffect } from 'react'
import api from '../../utils/api'
import { trustScoreColor } from '../../utils/trustScoreColor'
import { Users, Search, Star, AlertTriangle } from 'lucide-react'

const demoWorkers = [
  { id: 'w1', name: 'Ravi Kumar', phone: '+919876543210', platform: 'zomato', primary_zone_code: 'CHN-VEL-4B', trust_score: 78.5, fraud_strikes: 0, account_status: 'ACTIVE', avg_weekly_earnings: 4200, tenure_weeks: 24, is_verified_partner: false },
  { id: 'w2', name: 'Priya Sharma', phone: '+919876543211', platform: 'swiggy', primary_zone_code: 'CHN-ANN-2A', trust_score: 85.0, fraud_strikes: 0, account_status: 'ACTIVE', avg_weekly_earnings: 3900, tenure_weeks: 36, is_verified_partner: true },
  { id: 'w3', name: 'Arjun Reddy', phone: '+919876543212', platform: 'zomato', primary_zone_code: 'BLR-KOR-1A', trust_score: 92.0, fraud_strikes: 0, account_status: 'ACTIVE', avg_weekly_earnings: 4800, tenure_weeks: 52, is_verified_partner: true },
  { id: 'w4', name: 'Karthik Nair', phone: '+919876543213', platform: 'swiggy', primary_zone_code: 'MUM-AND-1A', trust_score: 55.0, fraud_strikes: 1, account_status: 'ACTIVE', avg_weekly_earnings: 4500, tenure_weeks: 8 },
  { id: 'w5', name: 'Suresh Yadav', phone: '+919876543214', platform: 'zomato', primary_zone_code: 'DEL-CON-1A', trust_score: 42.0, fraud_strikes: 2, account_status: 'ACTIVE', avg_weekly_earnings: 4080, tenure_weeks: 16 },
  { id: 'w6', name: 'Dinesh Kumar', phone: '+919876543215', platform: 'zomato', primary_zone_code: 'CHN-VEL-4B', trust_score: 18.0, fraud_strikes: 3, account_status: 'SUSPENDED', avg_weekly_earnings: 0, tenure_weeks: 4 },
]

export default function WorkerTrustTable() {
  const [workers, setWorkers] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/admin/workers')
      .then(r => setWorkers(r.data?.workers || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const data = workers.length ? workers : demoWorkers
  const filtered = data.filter(w =>
    w.name?.toLowerCase().includes(search.toLowerCase()) ||
    w.primary_zone_code?.toLowerCase().includes(search.toLowerCase()) ||
    w.phone?.includes(search)
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white flex items-center gap-2"><Users className="w-5 h-5" /> All Workers</h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search workers..." className="input-field pl-9 py-2 text-sm w-64" />
        </div>
      </div>

      <div className="glass-card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 text-gray-400 text-xs uppercase">
              <th className="px-4 py-3 text-left">Worker</th>
              <th className="px-4 py-3 text-left">Platform</th>
              <th className="px-4 py-3 text-left">Zone</th>
              <th className="px-4 py-3 text-center">Trust Score</th>
              <th className="px-4 py-3 text-center">Strikes</th>
              <th className="px-4 py-3 text-center">Tenure</th>
              <th className="px-4 py-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(w => {
              const ts = trustScoreColor(w.trust_score || 50)
              return (
                <tr key={w.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-shield-500/20 flex items-center justify-center text-xs font-bold text-shield-400">
                        {w.name?.charAt(0) || '?'}
                      </div>
                      <div>
                        <p className="text-white font-medium flex items-center gap-1">
                          {w.name}
                          {w.is_verified_partner && <Star className="w-3 h-3 text-amber-400" />}
                        </p>
                        <p className="text-xs text-gray-500">{w.phone?.slice(0, 6)}****</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-300 capitalize">{w.platform}</td>
                  <td className="px-4 py-3 text-gray-300 text-xs">{w.primary_zone_code}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${ts.bg} ${ts.text} border ${ts.border}`}>
                      {Math.round(w.trust_score || 0)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {w.fraud_strikes > 0 ? (
                      <span className="flex items-center justify-center gap-1 text-danger-400 text-xs">
                        <AlertTriangle className="w-3 h-3" /> {w.fraud_strikes}
                      </span>
                    ) : <span className="text-gray-500">0</span>}
                  </td>
                  <td className="px-4 py-3 text-center text-gray-400">{w.tenure_weeks}w</td>
                  <td className="px-4 py-3 text-center">
                    <span className={w.account_status === 'ACTIVE' ? 'badge-green' : w.account_status === 'SUSPENDED' ? 'badge-red' : 'badge-amber'}>
                      {w.account_status}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {filtered.length === 0 && <p className="text-center text-gray-500 py-8">No workers found</p>}
      </div>
    </div>
  )
}
