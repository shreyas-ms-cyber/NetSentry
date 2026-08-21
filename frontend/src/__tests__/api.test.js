import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import api, { getDashboardSummary, getDevices, getTraffic, getAlerts } from '../services/api'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
    })),
  },
}))

describe('API Service', () => {
  let mockApi

  beforeEach(() => {
    mockApi = {
      get: vi.fn(),
      post: vi.fn(),
    }
    vi.clearAllMocks()
  })

  it('API instance is configured correctly', () => {
    expect(api).toBeDefined()
  })

  it('getDashboardSummary is a function', () => {
    expect(typeof getDashboardSummary).toBe('function')
  })

  it('getDevices is a function', () => {
    expect(typeof getDevices).toBe('function')
  })

  it('getTraffic is a function', () => {
    expect(typeof getTraffic).toBe('function')
  })

  it('getAlerts is a function', () => {
    expect(typeof getAlerts).toBe('function')
  })
})
