import { useState, useEffect } from 'react'
import { useClaims } from '../hooks/useClaims'
import ClaimCard from '../components/claims/ClaimCard'
import ClaimTimeline from '../components/claims/ClaimTimeline'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import { formatCurrency } from '../utils/formatCurrency'
import { FileText, Clock, CheckCircle, IndianRupee, Filter } from 'lucide-react'

export default function ClaimsPage() {
  const { claims, stats, loading, refetch } = useClaims()
  const [filter, setFilter] = useState('ALL')
  const [selectedClaim, setSelectedClaim] = useState(null)

  // Demo claims if API returns empty
  const demoClaims = claims.length ? claims : [
    { id: 'demo-1', claim_type: 'HEAVY_RAIN', zone_code: 'CHN-VEL-4B', disruption_hours: 4, calculated_payout: 1120, actual_payout: 1120, confidence_score: 92, fraud_tier: 'GREEN', fraud_score: 8, status: 'PAID', claimed_at: '2026-03-30T11:00:00Z' },
    { id: 'demo-2', claim_type: 'AQI', zone_code: 'DEL-CON-1A', disruption_hours: 6, calculated_payout: 840, actual_payout: null, confidence_score: 55, fraud_tier: 'AMBER', fraud_score: 45, status: 'PENDING', claimed_at: '2026-03-29T09:00:00Z' },
    { id: 'demo-3', claim_type: 'FLOOD', zone_code: 'MUM-AND-1A', disruption_hours: 8, calculated_payout: 1600, actual_payout: 1600, confidence_score: 97, fraud_tier: 'GREEN', fraud_score: 3, status: 'PAID', claimed_at: '2026-03-25T14:00:00Z' },
  ]

  const s = claims.length ? stats : { total: 3, pending_count: 1, approved_count: 2, total_paid: 2720 }

  const filtered = filter === 'ALL' ? demoClaims : demoClaims.filter(c => c.status === filter)

  if (loading) return <LoadingSpinner text="Loading claims..." />

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 animate-slide-in">
        <h1 className="text-2xl font-display font-bold text-white">Claim History</h1>
        <p className="text-gray-400 mt-1">All your parametric claims with AI confidence scores.</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 stagger-children">
        {[
          { icon: FileText, label: 'Total Claims', value: s.total, color: 'text-white' },
          { icon: Clock, label: 'Pending', value: s.pending_count, color: 'text-alert-400' },
          { icon: CheckCircle, label: 'Approved', value: s.approved_count, color: 'text-safety-400' },
          { icon: IndianRupee, label: 'Total Received', value: formatCurrency(s.total_paid), color: 'text-safety-400' },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="stat-card flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0">
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div>
              <p className="text-xs text-gray-400">{label}</p>
              <p className={`text-xl font-bold ${color}`}>{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2 mb-6 animate-slide-in">
        <Filter className="w-4 h-4 text-gray-400" />
        {['ALL', 'PAID', 'APPROVED', 'PENDING', 'REJECTED'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filter === f ? 'bg-shield-600/30 text-white border border-shield-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
            {f}
          </button>
        ))}
      </div>

      {/* Claims List */}
      <div className="space-y-4 stagger-children">
        {filtered.map(claim => (
          <div key={claim.id} onClick={() => setSelectedClaim(selectedClaim?.id === claim.id ? null : claim)}>
            <ClaimCard claim={claim} />
            {selectedClaim?.id === claim.id && (
              <div className="mt-2 ml-4 animate-slide-in">
                <ClaimTimeline claim={claim} />
              </div>
            )}
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="glass-card p-12 text-center">
            <FileText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No claims found for this filter.</p>
          </div>
        )}
      </div>
    </div>
  )
}
