/**
 * Zone polygon matching logic
 * Maps lat/lng to the nearest LaborGuard zone
 */

const ZONES = [
  { code: 'CHN-VEL-4B', city: 'Chennai', area: 'Velachery', lat: 12.9815, lng: 80.2180 },
  { code: 'CHN-ANN-2A', city: 'Chennai', area: 'Anna Nagar', lat: 13.0850, lng: 80.2101 },
  { code: 'CHN-TNR-1A', city: 'Chennai', area: 'T. Nagar', lat: 13.0418, lng: 80.2341 },
  { code: 'CHN-ADY-3A', city: 'Chennai', area: 'Adyar', lat: 13.0012, lng: 80.2565 },
  { code: 'BLR-KOR-1A', city: 'Bengaluru', area: 'Koramangala', lat: 12.9352, lng: 77.6245 },
  { code: 'BLR-IND-2A', city: 'Bengaluru', area: 'Indiranagar', lat: 12.9784, lng: 77.6408 },
  { code: 'MUM-AND-1A', city: 'Mumbai', area: 'Andheri', lat: 19.1136, lng: 72.8697 },
  { code: 'MUM-BAN-2A', city: 'Mumbai', area: 'Bandra', lat: 19.0596, lng: 72.8295 },
  { code: 'HYD-HIB-1A', city: 'Hyderabad', area: 'HITEC City', lat: 17.4435, lng: 78.3772 },
  { code: 'DEL-CON-1A', city: 'Delhi', area: 'Connaught Place', lat: 28.6315, lng: 77.2167 },
]

export function findNearestZone(lat, lng) {
  let nearest = ZONES[0]
  let minDist = Infinity
  for (const zone of ZONES) {
    const d = haversine(lat, lng, zone.lat, zone.lng)
    if (d < minDist) { minDist = d; nearest = zone }
  }
  return { ...nearest, distance_km: minDist.toFixed(2) }
}

export function getZonesByCity(city) {
  return ZONES.filter(z => z.city === city)
}

export function getAllZones() { return ZONES }

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}
