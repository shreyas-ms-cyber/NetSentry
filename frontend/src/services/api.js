import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Dashboard APIs
export const getDashboardSummary = () => api.get('/dashboard/summary')
export const getDevices = () => api.get('/devices')
export const getDevice = (id) => api.get(`/devices/${id}`)
export const getDevicePorts = (id) => api.get(`/devices/${id}/ports`)
export const getPorts = (params) => api.get('/ports', { params })
export const getTraffic = (params) => api.get('/traffic', { params })
export const getAlerts = (params) => api.get('/alerts', { params })
export const getTopTalkers = (params) => api.get('/top-talkers', { params })
export const acknowledgeAlert = (id) => api.post(`/alerts/${id}/acknowledge`)

export default api
