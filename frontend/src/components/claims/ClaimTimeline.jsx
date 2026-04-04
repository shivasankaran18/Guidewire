import { CheckCircle, Clock, AlertTriangle, XCircle, CreditCard } from 'lucide-react'

const timelineSteps = [
  { icon: AlertTriangle, label: 'Trigger Detected', status: 'complete' },
  { icon: CheckCircle, label: 'Claim Created', status: 'complete' },
  { icon: Clock, label: 'Fraud Check', status: 'complete' },
  { icon: CreditCard, label: 'Payout', status: 'current' },
]

export default function ClaimTimeline({ claim }) {
  const steps = [...timelineSteps]
  if (claim?.status === 'PAID') steps[3].status = 'complete'
  else if (claim?.status === 'REJECTED') { steps[2].status = 'error'; steps[3].status = 'pending' }
  else if (claim?.status === 'PENDING') { steps[2].status = 'current'; steps[3].status = 'pending' }

  const statusStyle = (s) => {
    if (s === 'complete') return 'bg-safety-500/20 text-safety-400 border-safety-500/30'
    if (s === 'current') return 'bg-shield-500/20 text-shield-400 border-shield-500/30 animate-pulse'
    if (s === 'error') return 'bg-danger-500/20 text-danger-400 border-danger-500/30'
    return 'bg-white/5 text-gray-500 border-white/10'
  }

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2">
      {steps.map((step, i) => (
        <div key={i} className="flex items-center gap-2 shrink-0">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border ${statusStyle(step.status)}`}>
            <step.icon className="w-4 h-4" />
            <span className="text-xs font-medium">{step.label}</span>
          </div>
          {i < steps.length - 1 && <div className="w-4 h-px bg-white/20" />}
        </div>
      ))}
    </div>
  )
}
