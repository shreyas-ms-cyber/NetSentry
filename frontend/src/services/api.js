import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// Cache for API responses
const cache = new Map()
const CACHE_DURATION = 30000 // 30 seconds

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => Promise.reject(error)
)

// Cached GET function
const cachedGet = async (url, params = {}) => {
  const cacheKey = `${url}-${JSON.stringify(params)}`
  const cached = cache.get(cacheKey)
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }
  
  const response = await api.get(url, { params })
  cache.set(cacheKey, {
    data: response,
    timestamp: Date.now()
  })
  return response
}

// Dashboard APIs
export const getDashboardSummary = () => cachedGet('/dashboard/summary')
export const getDevices = () => cachedGet('/devices')
export const getDevice = (id) => cachedGet(`/devices/${id}`)
export const getDevicePorts = (id) => cachedGet(`/devices/${id}/ports`)
export const getPorts = (params) => cachedGet('/ports', params)
export const getTraffic = (params) => cachedGet('/traffic', params)
export const getAlerts = (params) => cachedGet('/alerts', params)

// Non-cached APIs (for mutations)
export const acknowledgeAlert = (id) => api.post(`/alerts/${id}/acknowledge`)

// Clear cache when needed
export const clearCache = () => {
  cache.clear()
}

export default api
