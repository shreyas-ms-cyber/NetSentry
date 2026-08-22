import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getTraffic } from '../services/api'
import './Traffic.css'

const Traffic = () => {
  const [loading, setLoading] = useState(true)
  const [trafficData, setTrafficData] = useState([])
  const [error, setError] = useState(null)
  const [displayData, setDisplayData] = useState(null)

  const fetchTraffic = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getTraffic({ limit: 200 })
      
      let data = []
      if (response && response.data) {
        data = Array.isArray(response.data) ? response.data : []
      }
      
      setTrafficData(data)
      
      // Find the best entry to display
      const bestEntry = findBestTrafficEntry(data)
      setDisplayData(bestEntry)
      
    } catch (err) {
      console.error('Error fetching traffic:', err)
      setError('Failed to load traffic data')
    } finally {
      setLoading(false)
    }
  }

  // Find the entry with the most recent non-zero protocol breakdown
  const findBestTrafficEntry = (data) => {
    if (!data || data.length === 0) return null
    
    // First, try to find an entry with non-zero protocol breakdown
    for (const entry of data) {
      const pb = entry.protocol_breakdown || {}
      if ((pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0) && 
          entry.packets_per_sec > 0) {
        return entry
      }
    }
    
    // If none found, return the first entry with packets_per_sec > 0
    for (const entry of data) {
      if (entry.packets_per_sec > 0) {
        return entry
      }
    }
    
    // Fallback to the first entry
    return data[0]
  }

  useEffect(() => {
    fetchTraffic()
  }, [])

  // Calculate stats from all data
  const calculateStats = () => {
    if (!trafficData || trafficData.length === 0) {
      return { totalPackets: 0, avgPps: 0, peakPps: 0, totalBandwidth: 0 }
    }
    const ppsValues = trafficData.map(d => typeof d.packets_per_sec === 'number' ? d.packets_per_sec : 0)
    const bandwidthValues = trafficData.map(d => typeof d.bandwidth_bytes === 'number' ? d.bandwidth_bytes : 0)
    return {
      totalPackets: trafficData.reduce((sum, d) => sum + (typeof d.total_packets === 'number' ? d.total_packets : 0), 0),
      avgPps: ppsValues.length > 0 ? ppsValues.reduce((a, b) => a + b, 0) / ppsValues.length : 0,
      peakPps: ppsValues.length > 0 ? Math.max(...ppsValues) : 0,
      totalBandwidth: bandwidthValues.reduce((a, b) => a + b, 0)
    }
  }

  const stats = calculateStats()
  const hasData = trafficData && trafficData.length > 0
  
  // Get protocol breakdown from display data
  const getProtocolBreakdown = () => {
    if (!displayData) return { tcp: 0, udp: 0, icmp: 0, other: 0 }
    const pb = displayData.protocol_breakdown || {}
    return {
      tcp: typeof pb.tcp === 'number' ? pb.tcp : 0,
      udp: typeof pb.udp === 'number' ? pb.udp : 0,
      icmp: typeof pb.icmp === 'number' ? pb.icmp : 0,
      other: typeof pb.other === 'number' ? pb.other : 0
    }
  }

  const getTopTalkers = () => {
    if (!displayData) return []
    const talkers = displayData.top_talkers
    return Array.isArray(talkers) ? talkers : []
  }

  const protocolBreakdown = getProtocolBreakdown()
  const topTalkers = getTopTalkers()
  const hasProtocolData = Object.values(protocolBreakdown).some(v => v > 0)

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

      {/* Traffic Timeline */}
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
        <div className="chart-container">
          {loading ? (
            <div className="chart-loading">Loading traffic data...</div>
          ) : hasData ? (
            <div className="chart-bars-wrapper">
              {trafficData.slice(0, 50).reverse().map((d, i) => {
                const pps = typeof d.packets_per_sec === 'number' ? d.packets_per_sec : 0
                const allPps = trafficData.map(t => typeof t.packets_per_sec === 'number' ? t.packets_per_sec : 0)
                const maxPps = Math.max(...allPps, 1)
                const height = Math.max(4, (pps / maxPps) * 90)
                return (
                  <div key={i} className="chart-bar-item">
                    <div 
                      className="chart-bar-fill" 
                      style={{ 
                        height: `${height}%`, 
                        backgroundColor: pps > 0 ? '#00E5FF' : 'rgba(255,255,255,0.05)' 
                      }} 
                    />
                    <span className="chart-bar-label">
                      {d.timestamp ? new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="chart-empty">
              <p>No traffic data available</p>
              <span>Start the Local Agent to begin monitoring</span>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="traffic-bottom-grid">
        {/* Protocol Breakdown - ALWAYS shows */}
        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Protocol Breakdown</div>
            <div className="chart-card-subtitle">Distribution</div>
          </div>
          <div className="protocol-list">
            {loading ? (
              <div className="protocol-loading">Loading...</div>
            ) : hasProtocolData ? (
              Object.entries(protocolBreakdown).map(([proto, value]) => (
                <div key={proto} className="protocol-item">
                  <span className="protocol-name">{proto.toUpperCase()}</span>
                  <div className="protocol-bar-track">
                    <div className="protocol-bar-fill" style={{ width: `${Math.max(1, value)}%` }} />
                  </div>
                  <span className="protocol-value">{value.toFixed(1)}%</span>
                </div>
              ))
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
          <div className="talkers-list">
            {loading ? (
              <div className="talkers-loading">Loading...</div>
            ) : topTalkers.length > 0 ? (
              topTalkers.slice(0, 5).map((talker, i) => {
                const maxBytes = topTalkers[0]?.bytes_mb || 1
                const bytes = typeof talker.bytes_mb === 'number' ? talker.bytes_mb : 0
                return (
                  <div key={i} className="talker-item">
                    <div className="talker-info">
                      <span className="talker-ip">{talker.ip || 'Unknown'}</span>
                      <span className="talker-traffic">{bytes.toFixed(1)} MB</span>
                    </div>
                    <div className="talker-bar-track">
                      <div 
                        className="talker-bar-fill" 
                        style={{ width: `${Math.min((bytes / maxBytes) * 100, 100)}%` }} 
                      />
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="talkers-empty">No traffic data available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Traffic
