import { useState, useEffect, useContext } from 'react'
import { WorkerContext } from '../context/WorkerContext'
import api from '../utils/api'

export function useWorkerProfile() {
  const ctx = useContext(WorkerContext)
  return ctx
}

export function useTrustScore() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetch = async () => {
    try {
      const res = await api.get('/api/workers/trust-score')
      setData(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])
  return { data, loading, refetch: fetch }
}
