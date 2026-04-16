import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../utils/api'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import { ArrowLeft, Clock, Shield, DollarSign, AlertTriangle, CheckCircle, XCircle, MessageSquare, FileText } from 'lucide-react'
import { formatCurrency } from '../utils/formatCurrency'

export default function ClaimDetailPage() {
  const { claimId } = useParams()
  const navigate = useNavigate()
  const [claim, setClaim] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadClaim()
  }, [claimId])

  const loadClaim = async () => {
    try {
      const res = await api.get(`/api/claims/${claimId}`)
      setClaim(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to load claim')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner text="Loading claim details..." />
  if (error) return (
    <div className="max-w-2xl mx-auto px-4 py-12 text-center">
      <AlertTriangle className="w-12 h-12 text-danger-400 mx-auto mb-4" />
      <h2 className="text-xl font-bold text-white mb-2">Error</h2>
      <p className="text-gray-400">{error}</p>
      <button onClick={() => navigate('/claims')} className="btn-primary mt-4">Back to Claims</button>
    </div>
  )

  const statusConfig = {
    PAID: { icon: CheckCircle, color: 'text-safety-400', bg: 'bg-safety-500/20', label: 'Paid' },
    APPROVED: { icon: CheckCircle, color: 'text-safety-400', bg: 'bg-safety-500/20', label: 'Approved' },
    PENDING: { icon: Clock, color: 'text-alert-400', bg: 'bg-alert-500/20', label: 'Pending Review' },
    APPEALED: { icon: MessageSquare, color: 'text-shield-400', bg: 'bg-shield-500/20', label: 'Under Appeal' },
    REJECTED: { icon: XCircle, color: 'text-danger-400', bg: 'bg-danger-500/20', label: 'Rejected' },
  }

  const tierColors = {
    GREEN: 'text-safety-400 bg-safety-500/20 border-safety-500/30',
    AMBER: 'text-alert-400 bg-alert-500/20 border-alert-500/30',
    RED: 'text-danger-400 bg-danger-500/20 border-danger-500/30',
  }

  const s = statusConfig[claim.status] || statusConfig.PENDING

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button onClick={() => navigate('/claims')} className="flex items-center gap-1 text-gray-400 hover:text-white text-sm mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Claims
      </button>

      <div className="animate-slide-in">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-2xl ${s.bg} flex items-center justify-center`}>
              <s.icon className={`w-7 h-7 ${s.color}`} />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold text-white">
                {claim.claim_type?.replace(/_/g, ' ')} Claim
              </h1>
              <p className="text-gray-400 text-sm">ID: {claim.id.slice(0, 12)}...</p>
            </div>
          </div>
          <div className="text-right">
            <span className={`px-3 py-1.5 rounded-lg text-sm font-medium border ${s.bg} ${s.color}`}>
              {s.label}
            </span>
            {claim.fraud_tier && (
              <span className={`ml-2 px-3 py-1.5 rounded-lg text-sm font-medium border ${tierColors[claim.fraud_tier]}`}>
                {claim.fraud_tier}
              </span>
            )}
          </div>
        </div>

        {/* Main Details */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-4">Claim Details</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Zone</span>
                <span className="text-white font-medium">{claim.zone_code}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Disruption Hours</span>
                <span className="text-white font-medium">{claim.disruption_hours} hrs</span>
              </div>
              {claim.claimed_at && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Filed On</span>
                  <span className="text-white font-medium">{new Date(claim.claimed_at).toLocaleDateString()}</span>
                </div>
              )}
              {claim.resolved_at && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Resolved On</span>
                  <span className="text-white font-medium">{new Date(claim.resolved_at).toLocaleDateString()}</span>
                </div>
              )}
              {claim.confidence_score !== null && (
                <div className="flex justify-between">
                  <span className="text-gray-400">AI Confidence</span>
                  <span className="text-white font-medium">{claim.confidence_score}%</span>
                </div>
              )}
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-4">Payout</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-400">Calculated Payout</span>
                <span className="text-white font-medium">{formatCurrency(claim.calculated_payout)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Actual Payout</span>
                <span className={claim.actual_payout ? 'text-safety-400 font-medium' : 'text-gray-500'}>
                  {claim.actual_payout ? formatCurrency(claim.actual_payout) : '—'}
                </span>
              </div>
              {claim.verification_method && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Verification</span>
                  <span className="text-white font-medium">{claim.verification_method}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="glass-card p-6 mb-8">
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-4">Timeline</h3>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-white/10" />
            <div className="space-y-6">
              <div className="relative pl-10">
                <div className="absolute left-2.5 w-3 h-3 rounded-full bg-shield-500 border-2 border-[#0f172a]" />
                <p className="text-white font-medium">Claim Filed</p>
                <p className="text-gray-400 text-sm">{claim.claimed_at ? new Date(claim.claimed_at).toLocaleString() : 'N/A'}</p>
              </div>
              {claim.status !== 'PENDING' && claim.status !== 'APPEALED' && (
                <div className="relative pl-10">
                  <div className={`absolute left-2.5 w-3 h-3 rounded-full border-2 border-[#0f172a] ${claim.status === 'REJECTED' ? 'bg-danger-500' : 'bg-safety-500'}`} />
                  <p className="text-white font-medium">
                    {claim.status === 'REJECTED' ? 'Rejected' : claim.status === 'APPROVED' ? 'Approved' : 'Paid'}
                  </p>
                  <p className="text-gray-400 text-sm">
                    {claim.resolved_at ? new Date(claim.resolved_at).toLocaleString() : claim.paid_at ? new Date(claim.paid_at).toLocaleString() : 'N/A'}
                  </p>
                </div>
              )}
              {claim.status === 'APPEALED' && (
                <div className="relative pl-10">
                  <div className="absolute left-2.5 w-3 h-3 rounded-full bg-shield-500 border-2 border-[#0f172a]" />
                  <p className="text-white font-medium">Under Appeal</p>
                  <p className="text-gray-400 text-sm">Awaiting manual review</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          {claim.status === 'REJECTED' && (
            <Link to={`/appeal/${claim.id}`} className="btn-primary flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Appeal This Decision
            </Link>
          )}
          {claim.status === 'PENDING' && (
            <Link to={`/appeal/${claim.id}`} className="btn-secondary flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Submit Appeal (Optional)
            </Link>
          )}
          <Link to="/claims" className="btn-secondary">Back to Claims</Link>
        </div>
      </div>
    </div>
  )
}