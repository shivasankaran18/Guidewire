import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../utils/api'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import { MessageCircle, Send, Sparkles, TrendingUp, Shield, DollarSign, Clock, MapPin, AlertTriangle } from 'lucide-react'

export default function WorkerAssistant() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your GigPulse AI Assistant. Ask me about your coverage, earnings, claims, or what to do during bad weather. How can I help?" }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [insights, setInsights] = useState(null)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadInsights()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadInsights = async () => {
    try {
      const [earningsRes, pricingRes] = await Promise.allSettled([
        api.get(`/api/agents/earnings-insight/${user.worker_id}`),
        api.get(`/api/agents/price-risk/${user.worker_id}`),
      ])
      setInsights({
        earnings: earningsRes.status === 'fulfilled' ? earningsRes.value.data.insight : null,
        pricing: pricingRes.status === 'fulfilled' ? pricingRes.value.data.pricing : null,
      })
    } catch (e) {
      console.error('Failed to load insights', e)
    } finally {
      setInsightsLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(m => [...m, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const res = await api.post('/api/agents/chat', { message: userMsg })
      const rawResponse = res.data.response
      let aiResponse = 'I understand. Let me help you with that.'
      
      if (rawResponse) {
        if (typeof rawResponse === 'string') {
          aiResponse = rawResponse
        } else if (typeof rawResponse === 'object') {
          aiResponse = rawResponse.answer || rawResponse.response || JSON.stringify(rawResponse)
        }
      }
      
      setMessages(m => [...m, { role: 'assistant', content: aiResponse }])
    } catch (e) {
      console.error('Chat error:', e)
      setMessages(m => [...m, { role: 'assistant', content: "Sorry, I'm having trouble connecting. Please try again." }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickActions = [
    "How much coverage do I have?",
    "What's my claim status?",
    "What triggers are active?",
    "How can I increase trust score?",
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 animate-slide-in">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-shield-500 to-shield-700 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-display font-bold text-white">AI Assistant</h1>
            <p className="text-gray-400 text-sm">Your personal coverage & earnings advisor</p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-card p-4 h-[500px] overflow-y-auto space-y-4">
            {messages.map((m, i) => {
              const content = typeof m.content === 'string' ? m.content : JSON.stringify(m.content)
              return (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-4 rounded-2xl ${
                    m.role === 'user' 
                      ? 'bg-shield-600/30 border border-shield-500/30 text-white' 
                      : 'bg-white/5 border border-white/10 text-gray-200'
                  }`}>
                    <div className="flex items-start gap-2">
                      {m.role === 'assistant' && <Sparkles className="w-4 h-4 text-shield-400 mt-0.5 shrink-0" />}
                      <p className="text-sm whitespace-pre-wrap">{content}</p>
                    </div>
                  </div>
                </div>
              )
            })}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/10 p-4 rounded-2xl">
                  <div className="flex items-center gap-2 text-gray-400">
                    <div className="w-2 h-2 rounded-full bg-shield-400 animate-pulse" />
                    <div className="w-2 h-2 rounded-full bg-shield-400 animate-pulse" style={{ animationDelay: '0.2s' }} />
                    <div className="w-2 h-2 rounded-full bg-shield-400 animate-pulse" style={{ animationDelay: '0.4s' }} />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 px-2">
            {quickActions.map((action, i) => (
              <button
                key={i}
                onClick={() => { setInput(action); setTimeout(handleSend, 100) }}
                className="px-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10 hover:text-white transition-all"
              >
                {action}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your coverage, claims, or earnings..."
              className="flex-1 input-field"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="btn-primary px-5 py-3 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
        </div>

        {/* Insights Panel */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-shield-400" />
            Your Insights
          </h2>

          {insightsLoading ? (
            <div className="glass-card p-6 text-center">
              <LoadingSpinner text="Analyzing..." />
            </div>
          ) : (
            <>
              {/* Earnings Insight */}
              {insights?.earnings && (
                <div className="glass-card p-5 border border-shield-500/30">
                  <div className="flex items-center gap-2 mb-3">
                    <DollarSign className="w-5 h-5 text-safety-400" />
                    <h3 className="font-semibold text-white">Earnings Analysis</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Daily Average</span>
                      <span className="text-white font-medium">₹{Number(insights.earnings.avg_daily_earnings || 0).toFixed(0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Weekly Average</span>
                      <span className="text-white font-medium">₹{Number(insights.earnings.avg_weekly_earnings || 0).toFixed(0)}</span>
                    </div>
                    {insights.earnings.estimated_payout && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Estimated Payout</span>
                        <span className="text-safety-400 font-medium">₹{Number(insights.earnings.estimated_payout).toFixed(0)}</span>
                      </div>
                    )}
                    {insights.earnings.risk_factors && Array.isArray(insights.earnings.risk_factors) && insights.earnings.risk_factors.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <p className="text-xs text-gray-400 mb-1">Risk Factors</p>
                        {insights.earnings.risk_factors.map((r, i) => (
                          <p key={i} className="text-xs text-alert-300">• {String(r)}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Risk Pricing */}
              {insights?.pricing && (
                <div className="glass-card p-5 border border-shield-500/30">
                  <div className="flex items-center gap-2 mb-3">
                    <Shield className="w-5 h-5 text-shield-400" />
                    <h3 className="font-semibold text-white">Premium Recommendation</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Recommended Tier</span>
                      <span className="text-white font-medium">{String(insights.pricing.recommended_tier || 'STANDARD')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Current Premium</span>
                      <span className="text-gray-300">₹{Number(insights.pricing.current_premium || 0).toFixed(0)}</span>
                    </div>
                    {insights.pricing.recommended_premium !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Recommended</span>
                        <span className="text-safety-400 font-medium">₹{Number(insights.pricing.recommended_premium).toFixed(0)}</span>
                      </div>
                    )}
                    {insights.pricing.live_events && Array.isArray(insights.pricing.live_events) && insights.pricing.live_events.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <p className="text-xs text-gray-400 mb-1">Live Events</p>
                        {insights.pricing.live_events.map((e, i) => (
                          <p key={i} className="text-xs text-alert-300">• {String(e)}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Fallback when no insights */}
              {!insights?.earnings && !insights?.pricing && (
                <div className="glass-card p-6 text-center border border-alert-500/20">
                  <AlertTriangle className="w-8 h-8 text-alert-400 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">Unable to load insights</p>
                  <p className="text-gray-500 text-xs mt-1">Make sure you have an active policy</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}