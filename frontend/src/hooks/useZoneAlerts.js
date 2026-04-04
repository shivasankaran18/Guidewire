import { useState, useEffect } from 'react'
import api from '../utils/api'

export function useZoneAlerts() {
  const [triggers, setTriggers] = useState([])
  const [weather, setWeather] = useState(null)
  const [aqi, setAqi] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetch = async () => {
    try {
      const res = await api.get('/api/triggers/status')
      setTriggers(res.data.active_triggers || [])
      setWeather(res.data.weather_current)
      setAqi(res.data.aqi_current)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])
  return { triggers, weather, aqi, loading, refetch: fetch }
}
