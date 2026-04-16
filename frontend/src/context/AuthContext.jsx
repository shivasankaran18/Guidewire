import { createContext, useState, useEffect } from 'react'
import api from '../utils/api'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('gs_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('gs_token')
      if (storedToken) {
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
        const stored = localStorage.getItem('gs_user')
        if (stored) {
          try { 
            setUser(JSON.parse(stored)) 
          } catch { 
            localStorage.removeItem('gs_token')
            localStorage.removeItem('gs_user')
            delete api.defaults.headers.common['Authorization']
            setToken(null)
          }
        }
      }
      setLoading(false)
    }
    initAuth()
  }, [])

  const login = async (authData) => {
    const { access_token, worker_id, role, name } = authData
    localStorage.setItem('gs_token', access_token)
    const userData = { worker_id, role, name }
    localStorage.setItem('gs_user', JSON.stringify(userData))
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setToken(access_token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('gs_token')
    localStorage.removeItem('gs_user')
    delete api.defaults.headers.common['Authorization']
    setToken(null)
    setUser(null)
  }

  const demoLogin = async () => {
    const res = await api.post('/api/auth/demo-login')
    await login(res.data)
    return res.data
  }

  const demoAdminLogin = async () => {
    const res = await api.post('/api/auth/demo-admin-login')
    await login(res.data)
    return res.data
  }

  const isAuthenticated = !!token && !loading && !!user

  return (
    <AuthContext.Provider value={{
      user, token, loading, isAuthenticated,
      login, logout, demoLogin, demoAdminLogin,
    }}>
      {children}
    </AuthContext.Provider>
  )
}
