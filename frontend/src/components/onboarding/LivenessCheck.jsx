import { useState, useRef, useEffect } from 'react'
import { Camera, CheckCircle, RefreshCw } from 'lucide-react'

export default function LivenessCheck({ onComplete }) {
  const [step, setStep] = useState('ready') // ready | capturing | processing | done
  const [progress, setProgress] = useState(0)
  const canvasRef = useRef(null)

  const startCapture = () => {
    setStep('capturing')
    setProgress(0)

    // Simulate liveness check stages
    const stages = [
      { pct: 20, label: 'Detecting face...' },
      { pct: 45, label: 'Checking blink...' },
      { pct: 65, label: 'Verifying depth...' },
      { pct: 85, label: 'Anti-spoof check...' },
      { pct: 100, label: 'Complete!' },
    ]

    let i = 0
    const interval = setInterval(() => {
      if (i < stages.length) {
        setProgress(stages[i].pct)
        i++
      } else {
        clearInterval(interval)
        setStep('done')
        onComplete?.({ liveness: true, confidence: 0.97 })
      }
    }, 600)
  }

  const reset = () => { setStep('ready'); setProgress(0) }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Camera className="w-5 h-5 text-shield-400" />
        <h3 className="text-sm font-semibold text-white">Selfie Liveness Check</h3>
      </div>

      <div className="glass-card p-6 flex flex-col items-center">
        {/* Camera Area */}
        <div className="w-40 h-40 rounded-full border-4 border-dashed border-white/20 flex items-center justify-center mb-4 relative overflow-hidden">
          {step === 'ready' && <Camera className="w-12 h-12 text-gray-500" />}
          {step === 'capturing' && (
            <>
              <div className="absolute inset-0 bg-shield-500/10 rounded-full" />
              <div className="w-16 h-16 border-4 border-shield-500/50 border-t-shield-500 rounded-full animate-spin" />
            </>
          )}
          {step === 'done' && (
            <div className="bg-safety-500/20 rounded-full w-full h-full flex items-center justify-center animate-scale-in">
              <CheckCircle className="w-16 h-16 text-safety-400" />
            </div>
          )}
        </div>

        {/* Progress */}
        {step === 'capturing' && (
          <div className="w-full max-w-xs mb-4">
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-shield-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">Analyzing... {progress}%</p>
          </div>
        )}

        {step === 'done' && (
          <div className="text-center animate-slide-in">
            <p className="text-safety-400 font-medium text-sm">✓ Liveness Verified</p>
            <p className="text-xs text-gray-400 mt-1">Confidence: 97% • Anti-spoof passed</p>
          </div>
        )}

        <div className="flex gap-3 mt-4">
          {step === 'ready' && (
            <button onClick={startCapture} className="btn-primary text-sm px-6 py-2">
              Start Liveness Check
            </button>
          )}
          {step === 'done' && (
            <button onClick={reset} className="btn-secondary text-sm px-4 py-2 flex items-center gap-1">
              <RefreshCw className="w-3 h-3" /> Retry
            </button>
          )}
        </div>

        <p className="text-[10px] text-gray-500 mt-3 text-center">
          Demo mode — no actual camera access required
        </p>
      </div>
    </div>
  )
}
