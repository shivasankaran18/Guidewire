import { useState, useEffect } from 'react'
import api from '../../utils/api'
import LoadingSpinner from '../shared/LoadingSpinner'
import { Sparkles, Search, Shield, AlertTriangle, MessageSquare, Users, FileSearch, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function AdminAIWorkbench() {
  const [section, setSection] = useState('investigate')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const sections = [
    { id: 'investigate', label: 'Claim Investigator', icon: FileSearch },
    { id: 'validate', label: 'Trigger Validator', icon: Shield },
    { id: 'ring', label: 'Fraud Ring Detective', icon: Users },
    { id: 'appeal', label: 'Appeal Handler', icon: MessageSquare },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-shield-500 to-shield-700 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">AI Workbench</h2>
          <p className="text-gray-400 text-sm">Run AI agents for fraud investigation and decision support</p>
        </div>
      </div>

      {/* Section Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {sections.map(s => (
          <button key={s.id} onClick={() => { setSection(s.id); setResult(null); setError(null) }}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${
              section === s.id ? 'bg-shield-600/30 text-white border border-shield-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
            <s.icon className="w-4 h-4" />{s.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="glass-card p-6">
        {section === 'investigate' && <ClaimInvestigator onResult={setResult} onError={setError} loading={loading} setLoading={setLoading} />}
        {section === 'validate' && <TriggerValidator onResult={setResult} onError={setError} loading={loading} setLoading={setLoading} />}
        {section === 'ring' && <RingInvestigator onResult={setResult} onError={setError} loading={loading} setLoading={setLoading} />}
        {section === 'appeal' && <AppealHandler onResult={setResult} onError={setError} loading={loading} setLoading={setLoading} />}
      </div>

      {/* Results */}
      {result && (
        <div className="glass-card p-6 border border-shield-500/30">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-shield-400" />
            <h3 className="font-semibold text-white">AI Analysis Result</h3>
          </div>
          <ResultDisplay result={result} />
        </div>
      )}

      {error && (
        <div className="glass-card p-6 border border-danger-500/30">
          <div className="flex items-center gap-2 text-danger-400">
            <AlertTriangle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      )}
    </div>
  )
}

function ResultDisplay({ result }) {
  if (!result) return null

  const isStructured = result.investigation || result.validation || result.investigation || result.decision

  if (isStructured) {
    const data = result.investigation || result.validation || result.investigation || result.decision

    return (
      <div className="space-y-4">
        {data.recommendation && (
          <div className={`p-4 rounded-xl border ${
            data.recommendation === 'APPROVE' ? 'bg-safety-500/10 border-safety-500/30' :
            data.recommendation === 'REJECT' ? 'bg-danger-500/10 border-danger-500/30' :
            'bg-alert-500/10 border-alert-500/30'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              {data.recommendation === 'APPROVE' && <CheckCircle className="w-5 h-5 text-safety-400" />}
              {data.recommendation === 'REJECT' && <XCircle className="w-5 h-5 text-danger-400" />}
              {data.recommendation === 'NEEDS_HUMAN' && <Clock className="w-5 h-5 text-alert-400" />}
              <span className={`font-semibold ${
                data.recommendation === 'APPROVE' ? 'text-safety-400' :
                data.recommendation === 'REJECT' ? 'text-danger-400' :
                'text-alert-400'
              }`}>
                Recommendation: {data.recommendation}
              </span>
            </div>
            {data.summary && <p className="text-gray-300 text-sm">{data.summary}</p>}
          </div>
        )}

        {data.confidence !== undefined && (
          <div className="flex items-center gap-4">
            <span className="text-gray-400">Confidence:</span>
            <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-shield-500 rounded-full" style={{ width: `${data.confidence}%` }} />
            </div>
            <span className="text-white font-medium">{data.confidence}%</span>
          </div>
        )}

        {data.key_findings && data.key_findings.length > 0 && (
          <div>
            <p className="text-gray-400 text-sm mb-2">Key Findings:</p>
            <ul className="space-y-1">
              {data.key_findings.map((f, i) => (
                <li key={i} className="text-gray-300 text-sm">• {f}</li>
              ))}
            </ul>
          </div>
        )}

        {data.signals && (
          <div>
            <p className="text-gray-400 text-sm mb-2">Fraud Signals:</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.signals).map(([key, val]) => (
                <span key={key} className="px-2 py-1 bg-white/5 rounded text-xs text-gray-300">
                  {key}: {String(val)}
                </span>
              ))}
            </div>
          </div>
        )}

        {data.explanation && (
          <div className="p-4 bg-white/5 rounded-xl">
            <p className="text-gray-300 text-sm whitespace-pre-wrap">{data.explanation}</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <pre className="text-gray-300 text-sm whitespace-pre-wrap overflow-x-auto">
      {JSON.stringify(result, null, 2)}
    </pre>
  )
}

function ClaimInvestigator({ onResult, onError, loading, setLoading }) {
  const [claimId, setClaimId] = useState('')

  const runInvestigation = async () => {
    if (!claimId.trim()) return
    setLoading(true)
    onError(null)
    try {
      const res = await api.post(`/api/agents/investigate/${claimId.trim()}`, {})
      onResult(res.data)
    } catch (e) {
      onError(e.response?.data?.detail || 'Investigation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-white">Claim Fraud Investigation</h3>
      <p className="text-gray-400 text-sm">Enter a claim ID to run AI fraud investigation analysis.</p>
      <div className="flex gap-3">
        <input
          value={claimId}
          onChange={(e) => setClaimId(e.target.value)}
          placeholder="Enter claim ID (e.g., claim-uuid)"
          className="flex-1 input-field"
        />
        <button onClick={runInvestigation} disabled={loading || !claimId.trim()} className="btn-primary px-5">
          {loading ? <LoadingSpinner text="" /> : 'Run Investigation'}
        </button>
      </div>
    </div>
  )
}

function TriggerValidator({ onResult, onError, loading, setLoading }) {
  const [triggerId, setTriggerId] = useState('')

  const runValidation = async () => {
    if (!triggerId.trim()) return
    setLoading(true)
    onError(null)
    try {
      const res = await api.post(`/api/agents/validate-trigger/${triggerId.trim()}`, {})
      onResult(res.data)
    } catch (e) {
      onError(e.response?.data?.detail || 'Validation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-white">Trigger Validation</h3>
      <p className="text-gray-400 text-sm">Enter a trigger ID to validate trigger reliability via AI cross-check.</p>
      <div className="flex gap-3">
        <input
          value={triggerId}
          onChange={(e) => setTriggerId(e.target.value)}
          placeholder="Enter trigger ID (e.g., trigger-uuid)"
          className="flex-1 input-field"
        />
        <button onClick={runValidation} disabled={loading || !triggerId.trim()} className="btn-primary px-5">
          {loading ? <LoadingSpinner text="" /> : 'Validate'}
        </button>
      </div>
    </div>
  )
}

function RingInvestigator({ onResult, onError, loading, setLoading }) {
  const runRingInvestigation = async () => {
    setLoading(true)
    onError(null)
    try {
      const res = await api.post('/api/agents/investigate-ring', {})
      onResult(res.data)
    } catch (e) {
      onError(e.response?.data?.detail || 'Ring investigation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-white">Fraud Ring Investigation</h3>
      <p className="text-gray-400 text-sm">Run AI analysis on all detected fraud rings with detailed evidence.</p>
      <button onClick={runRingInvestigation} disabled={loading} className="btn-primary px-5">
        {loading ? <LoadingSpinner text="" /> : 'Investigate All Rings'}
      </button>
    </div>
  )
}

function AppealHandler({ onResult, onError, loading, setLoading }) {
  const [claimId, setClaimId] = useState('')
  const [reason, setReason] = useState('')

  const runAppealHandler = async () => {
    if (!claimId.trim()) return
    setLoading(true)
    onError(null)
    try {
      const res = await api.post(`/api/agents/handle-appeal/${claimId.trim()}`, {
        appeal_reason: reason || 'Worker submitted appeal',
      })
      onResult(res.data)
    } catch (e) {
      onError(e.response?.data?.detail || 'Appeal handling failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-white">Appeal Resolution</h3>
      <p className="text-gray-400 text-sm">Enter claim ID + appeal reason for AI to re-evaluate the claim.</p>
      <input
        value={claimId}
        onChange={(e) => setClaimId(e.target.value)}
        placeholder="Enter claim ID (e.g., claim-uuid)"
        className="input-field w-full mb-3"
      />
      <textarea
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="Appeal reason (optional)"
        className="input-field w-full h-24 resize-none mb-3"
      />
      <button onClick={runAppealHandler} disabled={loading || !claimId.trim()} className="btn-primary px-5">
        {loading ? <LoadingSpinner text="" /> : 'Handle Appeal'}
      </button>
    </div>
  )
}