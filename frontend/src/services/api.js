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

// Response interceptor - always return { data: [], count: 0 } on error
api.interceptors.response.use(
  response => response,
  error => {
    // Return a consistent empty response instead of throwing
    return Promise.resolve({
      data: {
        devices: [],
        alerts: [],
        traffic: [],
        ports: [],
        count: 0,
        error: error.message || 'Request failed'
      }
    })
  }
)

// Cached GET function
const cachedGet = async (url, params = {}) => {
  const cacheKey = `${url}-${JSON.stringify(params)}`
  const cached = cache.get(cacheKey)
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }
  
  try {
    const response = await api.get(url, { params })
    // Ensure we always return an array
    const data = response.data || {}
    cache.set(cacheKey, {
      data: response,
      timestamp: Date.now()
    })
    return response
  } catch (error) {
    // Return a consistent empty response
    return {
      data: {
        devices: [],
        alerts: [],
        traffic: [],
        ports: [],
        count: 0
      }
    }
  }
}

// Dashboard APIs
export const getDashboardSummary = () => cachedGet('/dashboard/summary')
export const getDevices = () => cachedGet('/devices')
export const getDevice = (id) => cachedGet(`/devices/${id}`)
export const getDevicePorts = (id) => cachedGet(`/devices/${id}/ports`)
export const getPorts = (params) => cachedGet('/ports', params)
export const getTraffic = (params) => cachedGet('/traffic', params)
export const getAlerts = (params) => cachedGet('/alerts', params)

// Non-cached APIs
export const acknowledgeAlert = async (id) => {
  try {
    return await api.post(`/alerts/${id}/acknowledge`)
  } catch (error) {
    return { data: { status: 'error', message: error.message } }
  }
}

// Clear cache
export const clearCache = () => {
  cache.clear()
}

export default api
