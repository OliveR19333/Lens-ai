// Axios API client with auth + offline awareness (spec §3.1, §10.1).
import axios from 'axios'
import { useStore } from '../store/useStore'
import { cacheGeocode, getCachedGeocode } from '../db/parcelCache'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

export const api = axios.create({ baseURL, timeout: 30000 })

// Attach JWT to every request.
api.interceptors.request.use((config) => {
  const token = useStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Bounce to login on 401.
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) useStore.getState().logout()
    return Promise.reject(err)
  }
)

// ---- Endpoint wrappers (spec §4.2) ----

export async function login(username, password) {
  const { data } = await api.post('/auth/login', { username, password })
  return data // { access_token, token_type }
}

export async function listCounties() {
  const { data } = await api.get('/counties')
  return data
}

// Geocode with offline fallback to the IndexedDB cache (spec §3.2 / §10.1).
export async function geocode(address) {
  try {
    const { data } = await api.post('/geocode', { address })
    await cacheGeocode(address, data)
    return data
  } catch (err) {
    const cached = await getCachedGeocode(address)
    if (cached) return { ...cached, _offline: true }
    throw err
  }
}

export async function lookupParcel(lat, lng, county) {
  const { data } = await api.post('/parcel/lookup', { lat, lng, county })
  return data
}

export async function generateMission(parcelGeojson, opts = {}) {
  const { data } = await api.post('/mission/generate', {
    parcel_geojson: parcelGeojson,
    altitude_ft: opts.altitudeFt ?? 120,
    forward_overlap: opts.forwardOverlap ?? 0.8,
    side_overlap: opts.sideOverlap ?? 0.75,
    buffer_ft: opts.bufferFt ?? 15,
    project_id: opts.projectId
  })
  return data // { mission_id, summary, kmz_url }
}

export function kmzUrl(missionId) {
  return `${baseURL}/mission/${missionId}/kmz`
}

export async function createProject(payload) {
  const { data } = await api.post('/project/create', payload)
  return data
}

export async function uploadImages(projectId, files) {
  const form = new FormData()
  for (const f of files) form.append('images', f)
  const { data } = await api.post(`/project/${projectId}/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function projectStatus(projectId) {
  const { data } = await api.get(`/project/${projectId}/status`)
  return data
}

export async function projectMaps(projectId) {
  const { data } = await api.get(`/project/${projectId}/maps`)
  return data
}

export async function triggerFeatures(projectId) {
  const { data } = await api.post(`/project/${projectId}/features`)
  return data
}

export async function syncParcels() {
  const { data } = await api.get('/sync/parcels')
  return data
}
