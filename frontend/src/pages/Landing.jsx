import { Link } from 'react-router-dom'
import { Shield, Zap, Brain, Clock, IndianRupee, CloudRain, Thermometer, Wind, AlertTriangle, CheckCircle } from 'lucide-react'

const features = [
  { icon: Zap, title: 'Zero-Touch Claims', desc: 'No paperwork. Triggers fire automatically when disruptions hit your zone.' },
  { icon: Brain, title: 'AI Fraud Defense', desc: '7-signal fraud detection with DBSCAN ring detection. Your money is safe.' },
  { icon: Clock, title: 'Instant UPI Payout', desc: 'Money hits your UPI before you realize you lost income.' },
  { icon: IndianRupee, title: '₹29–75/week', desc: 'Dynamic pricing based on your zone risk. Fair, transparent, affordable.' },
]

const triggers = [
  { icon: CloudRain, label: 'Heavy Rain', threshold: '> 80mm/hr' },
  { icon: AlertTriangle, label: 'Flood Alert', threshold: 'IMD Red Alert' },
  { icon: Thermometer, label: 'Severe Heat', threshold: '> 43°C' },
  { icon: Wind, label: 'Hazardous AQI', threshold: 'AQI > 400' },
]

export default function Landing() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden py-20 px-4">
        <div className="absolute inset-0 bg-hero-pattern opacity-90" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#0f172a]" />
        <div className="relative max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-sm text-shield-200 mb-8 animate-fade-in">
            <Shield className="w-4 h-4" /> Built for Guidewire DEVTrails 2026
          </div>
          <h1 className="text-5xl md:text-7xl font-display font-extrabold text-white mb-6 leading-tight animate-slide-in">
            Income Protection<br />
            <span className="gradient-text">for Gig Workers</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-10 animate-slide-in" style={{ animationDelay: '0.1s' }}>
            AI-powered parametric insurance that automatically detects disruptions, 
            verifies claims, and pays delivery workers — before they even realize they've lost income.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-in" style={{ animationDelay: '0.2s' }}>
            <Link to="/login" className="btn-primary text-lg px-8 py-4">
              Get Protected →
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-4">
              Try Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Problem */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <div className="glass-card p-8 md:p-12">
          <h2 className="text-3xl font-display font-bold text-white mb-6">Meet Ravi 👤</h2>
          <p className="text-gray-300 text-lg leading-relaxed mb-6">
            Zomato delivery partner in Chennai earning ₹700/day. When Cyclone Fengal floods his zone, 
            Zomato suspends deliveries. Ravi loses <span className="text-danger-400 font-bold">₹2,000 in 3 days</span> with zero recourse.
          </p>
          <p className="text-gray-400">
            12+ million gig workers in India have no financial safety net. No ESIC, no PF, no insurance. 
            <span className="text-white font-semibold"> LaborGuard fixes this.</span>
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-display font-bold text-white text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 stagger-children">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="glass-card p-6 hover:border-shield-500/50 transition-all duration-300 group">
              <div className="w-12 h-12 rounded-xl bg-shield-500/20 flex items-center justify-center mb-4 group-hover:bg-shield-500/30 transition-colors">
                <Icon className="w-6 h-6 text-shield-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-gray-400">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Triggers */}
      <section className="py-20 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-display font-bold text-white text-center mb-4">5 Parametric Triggers</h2>
        <p className="text-gray-400 text-center mb-12">Monitored 24/7. No human intervention needed.</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {triggers.map(({ icon: Icon, label, threshold }) => (
            <div key={label} className="glass-card p-5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-alert-500/20 flex items-center justify-center shrink-0">
                <Icon className="w-5 h-5 text-alert-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">{label}</p>
                <p className="text-xs text-gray-400">{threshold}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Flow */}
      <section className="py-20 px-4 max-w-4xl mx-auto">
        <div className="glass-card p-8">
          <h2 className="text-2xl font-display font-bold text-white mb-8 text-center">The LaborGuard Flow</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {['ENROLL', 'MONITOR', 'TRIGGER', 'VERIFY', 'PAY'].map((step, i) => (
              <div key={step} className="flex items-center gap-3">
                <div className="px-5 py-3 rounded-xl bg-shield-500/20 border border-shield-500/30 text-shield-300 font-bold text-sm">
                  {step}
                </div>
                {i < 4 && <span className="text-shield-500 text-xl">→</span>}
              </div>
            ))}
          </div>
          <div className="flex flex-wrap justify-center gap-3 mt-4 text-xs text-gray-500">
            {['Weekly Premium', 'Real-time Zone Watch', 'Parametric Event', 'AI Fraud Defense', 'Instant UPI'].map((sub, i) => (
              <div key={sub} className="flex items-center gap-3">
                <span className="w-24 text-center">{sub}</span>
                {i < 4 && <span className="text-transparent text-xl">→</span>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 text-center">
        <h2 className="text-4xl font-display font-bold text-white mb-4">Ready to protect your income?</h2>
        <p className="text-gray-400 mb-8">Join LaborGuard. Starting at just ₹29/week.</p>
        <Link to="/login" className="btn-primary text-lg px-10 py-4">
          Start Now →
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-4 text-center text-gray-500 text-sm">
        <p>Built for Guidewire DEVTrails University Hackathon 2026 🚀</p>
        <p className="mt-1">Theme: Seed • Scale • Soar</p>
      </footer>
    </div>
  )
}
