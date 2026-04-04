import { useState, useEffect } from 'react'
import api from '../utils/api'

export function useClaims() {
  const [claims, setClaims] = useState([])
  const [stats, setStats] = useState({ total: 0, pending_count: 0, approved_count: 0, total_paid: 0 })
  const [loading, setLoading] = useState(true)

  const fetch = async () => {
    setLoading(true)
    try {
      const res = await api.get('/api/claims/')
      setClaims(res.data.claims || [])
      setStats({
        total: res.data.total,
        pending_count: res.data.pending_count,
        approved_count: res.data.approved_count,
        total_paid: res.data.total_paid,
      })
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])
  return { claims, stats, loading, refetch: fetch }
}
