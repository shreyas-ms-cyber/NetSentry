import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getTraffic } from '../services/api'
import TrafficChart from '../components/dashboard/TrafficChart'
import ProtocolChart from '../components/dashboard/ProtocolChart'
import BandwidthChart from '../components/dashboard/BandwidthChart'
import TopTalkers from '../components/dashboard/TopTalkers'
import './Traffic.css'

const Traffic = () => {
  const [loading, setLoading] = useState(true)
  const [trafficData, setTrafficData] = useState([])
  const [error, setError] = useState(null)

  const fetchTraffic = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getTraffic({ limit: 100 })

      let data = []
      if (response?.data) {
        if (Array.isArray(response.data)) {
          data = response.data
        } else if (response.data.traffic && Array.isArray(response.data.traffic)) {
          data = response.data.traffic
        }
      }

      console.log('Traffic Data:', data)
      setTrafficData(data)
    } catch (err) {
      console.error('Error fetching traffic:', err)
      setError('Failed to load traffic data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTraffic()
  }, [])

  // Find the best entry for protocol breakdown and top talkers
  const findDisplayEntry = () => {
    if (!trafficData || trafficData.length === 0) return null
    for (const entry of trafficData) {
      const pb = entry.protocol_breakdown || {}
      if (pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0) {
        return entry
      }
    }
    return trafficData[0] || null
  }

  // Calculate stats from all data
  const calculateStats = () => {
    if (!trafficData || trafficData.length === 0) {
      return { totalPackets: 0, avgPps: 0, peakPps: 0, totalBandwidth: 0 }
    }
    
    const ppsValues = trafficData.map(d => typeof d.packets_per_sec === 'number' ? d.packets_per_sec : 0)
    const bandwidthValues = trafficData.map(d => typeof d.bandwidth_bytes === 'number' ? d.bandwidth_bytes : 0)
    
    // Compute total packets from pps over time intervals
    let totalPackets = 0
    for (let i = 0; i < trafficData.length; i++) {
      const current = trafficData[i]
      const next = trafficData[i + 1]
      if (next && current.timestamp && next.timestamp) {
        const timeDiff = (new Date(next.timestamp) - new Date(current.timestamp)) / 1000 // seconds
        const avgPps = (current.packets_per_sec + next.packets_per_sec) / 2
        totalPackets += avgPps * timeDiff
      }
    }
    // If we have only one entry, approximate total packets as pps * 10 seconds (assumed interval)
    if (trafficData.length === 1) {
      totalPackets = trafficData[0].packets_per_sec * 10
    }

    return {
      totalPackets: Math.round(totalPackets),
      avgPps: ppsValues.length > 0 ? ppsValues.reduce((a, b) => a + b, 0) / ppsValues.length : 0,
      peakPps: ppsValues.length > 0 ? Math.max(...ppsValues) : 0,
      totalBandwidth: bandwidthValues.reduce((a, b) => a + b, 0)
    }
  }

  const displayEntry = findDisplayEntry()
  const stats = calculateStats()
  const hasData = trafficData && trafficData.length > 0

  const protocolBreakdown = displayEntry?.protocol_breakdown || { tcp: 0, udp: 0, icmp: 0, other: 0 }
  const topTalkers = displayEntry?.top_talkers || []
  const hasProtocolData = Object.values(protocolBreakdown).some(v => v > 0)

  console.log('Display Entry:', displayEntry)
  console.log('Protocol Breakdown:', protocolBreakdown)
  console.log('Top Talkers:', topTalkers)

  if (error) {
    return (
      <div className="traffic-page">
        <div className="traffic-error">
          <FontAwesomeIcon icon="exclamation-triangle" />
          <p>{error}</p>
          <button className="btn-retry" onClick={fetchTraffic}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="traffic-page">
      {/* Header */}
      <div className="traffic-header">
        <div>
          <h1 className="traffic-title">Network Traffic</h1>
          <p className="traffic-subtitle">Real-time network traffic analysis</p>
        </div>
        <button className="btn-refresh-traffic" onClick={fetchTraffic} disabled={loading}>
          <FontAwesomeIcon icon={loading ? 'spinner' : 'rotate'} spin={loading} />
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="traffic-stats">
        <div className="traffic-stat-card">
          <span className="stat-label">Total Packets</span>
          <span className="stat-value">{stats.totalPackets.toLocaleString()}</span>
        </div>
        <div className="traffic-stat-card">
          <span className="stat-label">Avg Packets/sec</span>
          <span className="stat-value">{stats.avgPps.toFixed(1)}</span>
        </div>
        <div className="traffic-stat-card">
          <span className="stat-label">Peak Packets/sec</span>
          <span className="stat-value">{stats.peakPps.toFixed(1)}</span>
        </div>
        <div className="traffic-stat-card">
          <span className="stat-label">Total Bandwidth</span>
          <span className="stat-value">{(stats.totalBandwidth / 1024 / 1024).toFixed(2)} MB</span>
        </div>
      </div>

      {/* Traffic Timeline - Using the same chart as Dashboard */}
      <div className="traffic-chart-card full-width">
        <div className="chart-card-header">
          <div>
            <div className="chart-card-title">Traffic Timeline</div>
            <div className="chart-card-subtitle">Packets per second over time</div>
          </div>
          {hasData && (
            <div className="chart-current">
              <span className="current-value">{stats.peakPps.toFixed(0)}</span>
              <span className="current-label">Peak pps</span>
            </div>
          )}
        </div>
        <TrafficChart data={trafficData} loading={loading} />
      </div>

      {/* Bottom Grid */}
      <div className="traffic-bottom-grid">
        {/* Protocol Breakdown */}
        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Protocol Breakdown</div>
            <div className="chart-card-subtitle">Distribution</div>
          </div>
          <div className="protocol-list">
            {loading ? (
              <div className="protocol-loading">Loading...</div>
            ) : hasProtocolData ? (
              Object.entries(protocolBreakdown).map(([proto, value]) => {
                const numValue = typeof value === 'number' ? value : 0
                return (
                  <div key={proto} className="protocol-item">
                    <span className="protocol-name">{proto.toUpperCase()}</span>
                    <div className="protocol-bar-track">
                      <div className="protocol-bar-fill" style={{ width: `${Math.max(1, numValue)}%` }} />
                    </div>
                    <span className="protocol-value">{numValue.toFixed(1)}%</span>
                  </div>
                )
              })
            ) : (
              <div className="protocol-empty">No protocol data available</div>
            )}
          </div>
        </div>

        {/* Top Talkers */}
        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Top Talkers</div>
            <div className="chart-card-subtitle">Traffic volume</div>
          </div>
          <TopTalkers data={topTalkers} loading={loading} />
        </div>
      </div>
    </div>
  )
}

export default Traffic
