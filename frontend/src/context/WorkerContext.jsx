import { createContext, useState, useEffect, useContext } from 'react'
import { AuthContext } from './AuthContext'
import api from '../utils/api'

export const WorkerContext = createContext(null)

export function WorkerProvider({ children }) {
  const { isAuthenticated, user } = useContext(AuthContext)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isAuthenticated && user?.role === 'WORKER') {
      fetchProfile()
    }
  }, [isAuthenticated])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      const res = await api.get('/api/workers/profile')
      setProfile(res.data)
    } catch (err) {
      console.error('Failed to fetch profile:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <WorkerContext.Provider value={{ profile, loading, fetchProfile }}>
      {children}
    </WorkerContext.Provider>
  )
}
