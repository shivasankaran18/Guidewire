import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Shield, MessageSquare, CheckCircle, ArrowLeft } from 'lucide-react'
import api from '../utils/api'

const quickReasons = [
  'I was actively delivering during this time — GPS data can confirm.',
  'My phone battery died so GPS data is incomplete, but I was working.',
  'The weather disruption was worse than sensors reported in my area.',
  'Platform orders were down in my sub-zone even if other zones were active.',
]

export default function AppealPage() {
  const { claimId } = useParams()
  const navigate = useNavigate()
  const [reason, setReason] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (reason.length < 10) { setError('Please provide at least 10 characters.'); return }
    setLoading(true)
    setError('')
    try {
      await api.post(`/api/claims/appeal/${claimId}`, { reason })
      setSubmitted(true)
    } catch (e) {
      setError(e.response?.data?.detail || 'Appeal submission failed')
    } finally { setLoading(false) }
  }

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center animate-scale-in">
        <div className="w-20 h-20 rounded-full bg-safety-500/20 flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-safety-400" />
        </div>
        <h1 className="text-2xl font-display font-bold text-white mb-3">Appeal Submitted! 🛡️</h1>
        <p className="text-gray-400 mb-2">Your appeal is being reviewed by our team.</p>
        <p className="text-gray-500 text-sm mb-8">You'll hear back within <span className="text-white font-semibold">2 hours</span>. If we were wrong, a ₹50 goodwill credit is added.</p>
        <button onClick={() => navigate('/claims')} className="btn-primary">
          Back to Claims →
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-400 hover:text-white text-sm mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="animate-slide-in">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-shield-500/20 flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-shield-400" />
          </div>
          <div>
            <h1 className="text-2xl font-display font-bold text-white">One-Tap Appeal</h1>
            <p className="text-sm text-gray-400">Claim ID: {claimId?.slice(0, 8)}...</p>
          </div>
        </div>
      </div>

      <div className="glass-card p-6 mt-6 animate-slide-in" style={{ animationDelay: '0.1s' }}>
        <div className="bg-shield-500/10 border border-shield-500/20 rounded-xl p-4 mb-6">
          <p className="text-sm text-shield-300 font-medium mb-1">🛡️ Fair Appeal Guarantee</p>
          <p className="text-xs text-gray-400">If our AI was wrong and your claim is valid, you receive your full payout + ₹50 goodwill credit. Manual review within 2 hours.</p>
        </div>

        <h3 className="text-sm font-semibold text-white mb-3">Quick Reasons (tap to select)</h3>
        <div className="space-y-2 mb-6">
          {quickReasons.map((r, i) => (
            <button
              key={i}
              onClick={() => setReason(r)}
              className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-all border ${reason === r
                ? 'bg-shield-500/20 border-shield-500/40 text-white'
                : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10'}`}
            >
              {r}
            </button>
          ))}
        </div>

        <h3 className="text-sm font-semibold text-white mb-2">Or write your own</h3>
        <textarea
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="Explain why this claim should be approved..."
          rows={4}
          className="input-field resize-none mb-2"
        />
        <p className="text-xs text-gray-500 mb-4">{reason.length}/500 characters</p>

        {error && <p className="text-danger-400 text-sm mb-4">{error}</p>}

        <button onClick={handleSubmit} disabled={loading || reason.length < 10} className="btn-primary w-full">
          {loading ? 'Submitting...' : 'Submit Appeal'}
        </button>
      </div>
    </div>
  )
}
