import { trustScoreColor } from '../../utils/trustScoreColor'
import { Star } from 'lucide-react'

export default function TrustScoreBadge({ score = 50, strikes = 0 }) {
  const { bg, text, border, label } = trustScoreColor(score)

  return (
    <div className="glass-card p-6">
      <p className="text-xs text-gray-400 uppercase tracking-wider mb-3">Trust Score</p>
      <div className="flex items-center gap-4">
        <div className="relative w-16 h-16">
          <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="15.5" fill="none" className="stroke-white/10" strokeWidth="3" />
            <circle cx="18" cy="18" r="15.5" fill="none" className={`${text.replace('text-', 'stroke-')}`} strokeWidth="3" strokeDasharray={`${score} ${100 - score}`} strokeLinecap="round" />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-lg font-bold text-white">{Math.round(score)}</span>
        </div>
        <div>
          <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${bg} ${text} border ${border}`}>
            {score >= 80 && <Star className="w-3 h-3" />}
            {label}
          </div>
          {strikes > 0 && (
            <p className="text-xs text-danger-400 mt-2">⚠️ {strikes} fraud strike{strikes > 1 ? 's' : ''}</p>
          )}
        </div>
      </div>
    </div>
  )
}
