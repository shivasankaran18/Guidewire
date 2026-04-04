import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import OTPInput from '../components/shared/OTPInput'
import { Shield, Phone, ArrowRight, Sparkles } from 'lucide-react'
import api from '../utils/api'

export default function Login() {
  const [step, setStep] = useState('phone') // phone | otp
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [demoOtp, setDemoOtp] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, demoLogin, demoAdminLogin } = useAuth()
  const navigate = useNavigate()

  const sendOtp = async () => {
    setError('')
    setLoading(true)
    try {
      const fullPhone = phone.startsWith('+91') ? phone : `+91${phone}`
      const res = await api.post('/api/auth/send-otp', { phone: fullPhone })
      // Extract demo OTP from message
      const match = res.data.message?.match(/Demo OTP: (\d{6})/)
      if (match) setDemoOtp(match[1])
      setStep('otp')
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to send OTP')
    } finally { setLoading(false) }
  }

  const verifyOtp = async (otpValue) => {
    setError('')
    setLoading(true)
    try {
      const fullPhone = phone.startsWith('+91') ? phone : `+91${phone}`
      const res = await api.post('/api/auth/verify-otp', { phone: fullPhone, otp: otpValue })
      await login(res.data)
      navigate('/dashboard')
    } catch (e) {
      setError(e.response?.data?.detail || 'Invalid OTP')
    } finally { setLoading(false) }
  }

  const handleDemo = async (isAdmin = false) => {
    setLoading(true)
    try {
      if (isAdmin) await demoAdminLogin()
      else await demoLogin()
      navigate(isAdmin ? '/admin' : '/dashboard')
    } catch (e) {
      setError('Demo login failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-hero-pattern">
      <div className="w-full max-w-md">
        <div className="text-center mb-8 animate-slide-in">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-shield-500 to-shield-700 flex items-center justify-center mx-auto mb-4 shadow-neon-blue">
            <Shield className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-display font-bold text-white">LaborGuard</h1>
          <p className="text-gray-400 mt-1">Income protection for gig workers</p>
        </div>

        <div className="glass-card p-8 animate-slide-in" style={{ animationDelay: '0.1s' }}>
          {step === 'phone' ? (
            <>
              <h2 className="text-xl font-semibold text-white mb-6">Login with OTP</h2>
              <div className="relative mb-4">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  placeholder="Enter phone number"
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                  className="input-field pl-11"
                  maxLength={13}
                />
              </div>
              <p className="text-xs text-gray-500 mb-4">Format: 9876543210 or +919876543210</p>
              {error && <p className="text-danger-400 text-sm mb-4">{error}</p>}
              <button onClick={sendOtp} disabled={loading || phone.length < 10} className="btn-primary w-full flex items-center justify-center gap-2">
                {loading ? 'Sending...' : 'Send OTP'} <ArrowRight className="w-4 h-4" />
              </button>
            </>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-white mb-2">Enter OTP</h2>
              <p className="text-gray-400 text-sm mb-6">Sent to +91{phone.replace('+91', '')}</p>
              {demoOtp && (
                <div className="bg-shield-500/10 border border-shield-500/30 rounded-lg px-4 py-2 mb-4 text-sm text-shield-300 text-center">
                  Demo OTP: <span className="font-bold text-white">{demoOtp}</span>
                </div>
              )}
              <OTPInput length={6} onComplete={verifyOtp} />
              {error && <p className="text-danger-400 text-sm mt-4 text-center">{error}</p>}
              <button onClick={() => setStep('phone')} className="text-shield-400 text-sm mt-4 block mx-auto hover:underline">
                ← Change number
              </button>
            </>
          )}
        </div>

        {/* Demo buttons */}
        <div className="mt-6 space-y-3 animate-slide-in" style={{ animationDelay: '0.2s' }}>
          <div className="text-center text-gray-500 text-sm">— Quick Demo Access —</div>
          <button onClick={() => handleDemo(false)} className="btn-secondary w-full flex items-center justify-center gap-2">
            <Sparkles className="w-4 h-4 text-shield-400" /> Demo as Ravi (Worker)
          </button>
          <button onClick={() => handleDemo(true)} className="btn-secondary w-full flex items-center justify-center gap-2">
            <Sparkles className="w-4 h-4 text-alert-400" /> Demo as Admin
          </button>
        </div>

        <p className="text-center text-gray-600 text-xs mt-6">
          Don't have an account? <a href="/onboarding" className="text-shield-400 hover:underline">Register here</a>
        </p>
      </div>
    </div>
  )
}
