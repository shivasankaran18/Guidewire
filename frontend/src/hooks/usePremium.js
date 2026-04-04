import { useState, useEffect } from 'react'
import api from '../utils/api'

export function usePremium() {
  const [plans, setPlans] = useState([])
  const [currentPolicy, setCurrentPolicy] = useState(null)
  const [hasActive, setHasActive] = useState(false)
  const [loading, setLoading] = useState(true)

  const fetchPlans = async () => {
    try {
      const res = await api.get('/api/policies/plans')
      setPlans(res.data.plans || [])
    } catch (e) { console.error(e) }
  }

  const fetchCurrent = async () => {
    try {
      const res = await api.get('/api/policies/current')
      setHasActive(res.data.has_active_policy)
      setCurrentPolicy(res.data.policy)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const activate = async (planTier) => {
    const res = await api.post('/api/policies/activate', { plan_tier: planTier })
    await fetchCurrent()
    return res.data
  }

  useEffect(() => { fetchPlans(); fetchCurrent() }, [])
  return { plans, currentPolicy, hasActive, loading, activate, refetch: fetchCurrent }
}
