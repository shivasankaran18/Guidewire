import { useState } from 'react'
import { Smartphone, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import api from '../../utils/api'

export default function WorkerIDVerify({ workerId, platform, onVerified }) {
  const [status, setStatus] = useState('idle') // idle | checking | verified | failed
  const [result, setResult] = useState(null)

  const verify = async () => {
    if (!workerId || workerId.length < 3) return
    setStatus('checking')
    try {
      const res = await api.get(`/mock/zomato/verify-worker?worker_id=${workerId}`)
      if (res.data.verified) {
        setStatus('verified')
        setResult(res.data)
        onVerified?.(res.data)
      } else {
        setStatus('failed')
        setResult(res.data)
      }
    } catch {
      setStatus('failed')
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Smartphone className="w-5 h-5 text-shield-400" />
        <h3 className="text-sm font-semibold text-white">Worker ID Verification</h3>
      </div>

      <div className="flex gap-2">
        <div className="flex-1 relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 uppercase">{platform || 'Zomato'}</span>
          <input
            value={workerId || ''}
            readOnly
            className="input-field pl-20 text-sm"
          />
        </div>
        <button onClick={verify} disabled={status === 'checking' || !workerId} className="btn-primary text-sm px-4 py-2">
          {status === 'checking' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Verify'}
        </button>
      </div>

      {status === 'verified' && (
        <div className="flex items-center gap-3 bg-safety-500/10 border border-safety-500/20 rounded-xl p-4 animate-slide-in">
          <CheckCircle className="w-6 h-6 text-safety-400 shrink-0" />
          <div>
            <p className="text-sm font-medium text-white">Worker Verified ✓</p>
            <p className="text-xs text-gray-400">
              {result?.name} • {result?.city} • Rating: {result?.rating} ⭐ • {result?.total_deliveries?.toLocaleString()} deliveries
            </p>
          </div>
        </div>
      )}

      {status === 'failed' && (
        <div className="flex items-center gap-3 bg-danger-500/10 border border-danger-500/20 rounded-xl p-4 animate-slide-in">
          <XCircle className="w-6 h-6 text-danger-400 shrink-0" />
          <div>
            <p className="text-sm font-medium text-white">Verification Failed</p>
            <p className="text-xs text-gray-400">Worker ID not found on {platform || 'Zomato'}. Please check and try again.</p>
          </div>
        </div>
      )}
    </div>
  )
}
