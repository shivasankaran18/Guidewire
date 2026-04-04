import { useState } from 'react'
import { CreditCard, Eye, EyeOff, Shield, Lock } from 'lucide-react'

export default function KYCForm({ aadhaar, upiId, onAadhaarChange, onUpiChange }) {
  const [showAadhaar, setShowAadhaar] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <CreditCard className="w-5 h-5 text-shield-400" />
        <h3 className="text-sm font-semibold text-white">Masked Aadhaar KYC</h3>
      </div>

      <div className="bg-shield-500/10 border border-shield-500/20 rounded-xl p-3 flex items-start gap-2">
        <Lock className="w-4 h-4 text-shield-400 mt-0.5 shrink-0" />
        <p className="text-xs text-shield-300">
          We store only the <strong>last 4 digits</strong> of your Aadhaar as a SHA-256 hash. 
          Your full number is never stored or transmitted. AES-256 encryption at rest.
        </p>
      </div>

      {/* Aadhaar Input */}
      <div>
        <label className="text-xs text-gray-400 block mb-1">Last 4 digits of Aadhaar</label>
        <div className="relative">
          <input
            type={showAadhaar ? 'text' : 'password'}
            value={aadhaar || ''}
            onChange={e => {
              const val = e.target.value.replace(/\D/g, '').slice(0, 4)
              onAadhaarChange?.(val)
            }}
            placeholder="XXXX"
            maxLength={4}
            className="input-field pr-10 text-lg tracking-[0.5em] text-center font-mono"
          />
          <button
            onClick={() => setShowAadhaar(!showAadhaar)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
          >
            {showAadhaar ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        {aadhaar?.length === 4 && (
          <p className="text-xs text-safety-400 mt-1 flex items-center gap-1">
            <Shield className="w-3 h-3" /> Masked Aadhaar: XXXX-XXXX-{aadhaar}
          </p>
        )}
      </div>

      {/* UPI Input */}
      <div>
        <label className="text-xs text-gray-400 block mb-1">UPI ID (for payouts)</label>
        <input
          type="text"
          value={upiId || ''}
          onChange={e => onUpiChange?.(e.target.value)}
          placeholder="yourname@upi"
          className="input-field text-sm"
        />
        {upiId && (
          <p className="text-xs text-gray-400 mt-1">
            Stored as: {upiId.split('@')[0]?.slice(0, 4)}****@{upiId.split('@')[1] || 'upi'}
          </p>
        )}
      </div>

      <div className="flex gap-2 text-xs text-gray-500">
        <span className="badge bg-white/10 text-gray-300 border border-white/10">🔐 AES-256</span>
        <span className="badge bg-white/10 text-gray-300 border border-white/10">🔒 SHA-256 Hash</span>
        <span className="badge bg-white/10 text-gray-300 border border-white/10">📋 DPDPA Compliant</span>
      </div>
    </div>
  )
}
