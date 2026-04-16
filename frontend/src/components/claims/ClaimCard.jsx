import { formatCurrency } from '../../utils/formatCurrency'
import { fraudTierColor } from '../../utils/trustScoreColor'
import { Clock, CheckCircle, XCircle, AlertTriangle, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const statusIcons = { PAID: CheckCircle, APPROVED: CheckCircle, PENDING: Clock, REJECTED: XCircle, APPEALED: AlertTriangle }
const statusColors = { PAID: 'text-safety-400', APPROVED: 'text-safety-400', PENDING: 'text-alert-400', REJECTED: 'text-danger-400', APPEALED: 'text-shield-400' }

export default function ClaimCard({ claim }) {
  const Icon = statusIcons[claim.status] || Clock
  const color = statusColors[claim.status] || 'text-gray-400'
  const tier = fraudTierColor(claim.fraud_tier)

  return (
    <div className="glass-card p-5 hover:bg-white/10 transition-all duration-300 group">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${tier.bg}`}>
            <Icon className={`w-5 h-5 ${color}`} />
          </div>
          <div>
            <Link to={`/claims/${claim.id}`} className="text-sm font-semibold text-white hover:text-shield-400 transition-colors">
              {claim.claim_type?.replace(/_/g, ' ')}
            </Link>
            <p className="text-xs text-gray-400 mt-0.5">Zone: {claim.zone_code} • {claim.disruption_hours}h disrupted</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-white">{formatCurrency(claim.actual_payout || claim.calculated_payout)}</p>
          <span className={`text-xs ${tier.text}`}>{tier.label}</span>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="mt-4 pt-3 border-t border-white/5">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Confidence: {claim.confidence_score || (100 - (claim.fraud_score || 0))}%</span>
          <span className={`font-medium ${color}`}>{claim.status}</span>
        </div>
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${claim.fraud_tier === 'GREEN' ? 'bg-safety-500' : claim.fraud_tier === 'AMBER' ? 'bg-alert-500' : 'bg-danger-500'}`}
               style={{ width: `${claim.confidence_score || (100 - (claim.fraud_score || 0))}%` }} />
        </div>
      </div>

      <div className="flex items-center justify-between mt-3">
        <Link to={`/claims/${claim.id}`} className="flex items-center gap-1 text-xs text-shield-400 group-hover:underline">
          View Details <ArrowRight className="w-3 h-3" />
        </Link>
        {(claim.status === 'REJECTED' || claim.status === 'PENDING') && (
          <Link to={`/appeal/${claim.id}`} className="flex items-center gap-1 text-xs text-alert-400 hover:text-alert-300">
            Appeal <ArrowRight className="w-3 h-3" />
          </Link>
        )}
      </div>
    </div>
  )
}
