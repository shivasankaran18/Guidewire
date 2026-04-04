import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Shield, User, Smartphone, MapPin, CreditCard, Camera, CheckCircle } from 'lucide-react'
import api from '../utils/api'
import { getAllZones } from '../utils/zonePolygon'

const steps = ['ID Verify', 'KYC', 'Zone', 'Complete']

export default function Onboarding() {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState({ name: '', phone: '', platform: 'zomato', platform_worker_id: '', aadhaar_last4: '', upi_id: '', zone_code: 'CHN-VEL-4B' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const zones = getAllZones()

  const update = (key, val) => setForm(prev => ({ ...prev, [key]: val }))

  const handleRegister = async () => {
    setError('')
    setLoading(true)
    try {
      const phone = form.phone.startsWith('+91') ? form.phone : `+91${form.phone}`
      const res = await api.post('/api/auth/register', { ...form, phone })
      await login(res.data)
      setStep(3)
    } catch (e) {
      setError(e.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-hero-pattern">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-shield-500 to-shield-700 flex items-center justify-center mx-auto mb-4 shadow-neon-blue">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-display font-bold text-white">Join LaborGuard</h1>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${i <= step ? 'bg-shield-500 text-white' : 'bg-white/10 text-gray-500'}`}>
                {i < step ? <CheckCircle className="w-4 h-4" /> : i + 1}
              </div>
              {i < steps.length - 1 && <div className={`w-8 h-0.5 ${i < step ? 'bg-shield-500' : 'bg-white/10'}`} />}
            </div>
          ))}
        </div>

        <div className="glass-card p-8 animate-slide-in">
          {step === 0 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2"><Smartphone className="w-5 h-5 text-shield-400" /> Worker ID Verification</h2>
              <input placeholder="Full Name" value={form.name} onChange={e => update('name', e.target.value)} className="input-field" />
              <input placeholder="Phone (10 digits)" value={form.phone} onChange={e => update('phone', e.target.value)} className="input-field" maxLength={13} />
              <select value={form.platform} onChange={e => update('platform', e.target.value)} className="input-field">
                <option value="zomato">Zomato</option>
                <option value="swiggy">Swiggy</option>
              </select>
              <input placeholder="Platform Worker ID (e.g. ZW123456)" value={form.platform_worker_id} onChange={e => update('platform_worker_id', e.target.value)} className="input-field" />
              <button onClick={() => setStep(1)} disabled={!form.name || !form.phone || !form.platform_worker_id} className="btn-primary w-full">Next →</button>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2"><CreditCard className="w-5 h-5 text-shield-400" /> Masked Aadhaar KYC</h2>
              <p className="text-xs text-gray-400">Only last 4 digits stored. Never the full number.</p>
              <input placeholder="Last 4 digits of Aadhaar" value={form.aadhaar_last4} onChange={e => update('aadhaar_last4', e.target.value)} className="input-field" maxLength={4} />
              <input placeholder="UPI ID (e.g. ravi@upi)" value={form.upi_id} onChange={e => update('upi_id', e.target.value)} className="input-field" />
              <div className="glass-card p-4 text-center">
                <Camera className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-xs text-gray-500">Selfie Liveness Check</p>
                <p className="text-xs text-safety-400 mt-1">✓ Simulated for demo</p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setStep(0)} className="btn-secondary flex-1">← Back</button>
                <button onClick={() => setStep(2)} className="btn-primary flex-1">Next →</button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2"><MapPin className="w-5 h-5 text-shield-400" /> Select Delivery Zone</h2>
              <p className="text-xs text-gray-400">500m polygon precision. This determines your premium.</p>
              <select value={form.zone_code} onChange={e => update('zone_code', e.target.value)} className="input-field">
                {zones.map(z => (
                  <option key={z.code} value={z.code}>{z.city} — {z.area} ({z.code})</option>
                ))}
              </select>
              {error && <p className="text-danger-400 text-sm">{error}</p>}
              <div className="flex gap-3">
                <button onClick={() => setStep(1)} className="btn-secondary flex-1">← Back</button>
                <button onClick={handleRegister} disabled={loading} className="btn-primary flex-1">{loading ? 'Registering...' : 'Complete Registration'}</button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="text-center py-8">
              <div className="w-16 h-16 rounded-full bg-safety-500/20 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-safety-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Welcome to LaborGuard! 🛡️</h2>
              <p className="text-gray-400 mb-6">Your account is set up. You're in a 2-week probation period.</p>
              <button onClick={() => navigate('/dashboard')} className="btn-primary">Go to Dashboard →</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
