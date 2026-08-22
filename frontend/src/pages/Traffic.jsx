import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getTraffic } from '../services/api'
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
      
      // The response data is the array of traffic entries
      let data = []
      if (response && response.data) {
        // response.data is the array of traffic entries
        data = Array.isArray(response.data) ? response.data : []
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

  // Find the best entry to display - one with non-zero protocol breakdown
  const findDisplayEntry = () => {
    if (!trafficData || trafficData.length === 0) return null
    
    // Find first entry with non-zero protocol breakdown
    for (const entry of trafficData) {
      if (entry.protocol_breakdown) {
        const pb = entry.protocol_breakdown
        if (pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0) {
          return entry
        }
      }
    }
    
    // If none found, return the latest entry
    return trafficData[0] || null
  }

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

  const displayEntry = findDisplayEntry()
  const stats = calculateStats()
  const hasData = trafficData && trafficData.length > 0

  // Get protocol breakdown from display entry
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
        {/* Protocol Breakdown */}
        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Protocol Breakdown</div>
            <div className="chart-card-subtitle">Distribution</div>
          </div>
          <div className="protocol-list">
            {loading ? (
              <div className="protocol-loading">Loading...</div>
            ) : (
              Object.entries(protocolBreakdown).map(([proto, value]) => (
                <div key={proto} className="protocol-item">
                  <span className="protocol-name">{proto.toUpperCase()}</span>
                  <div className="protocol-bar-track">
                    <div className="protocol-bar-fill" style={{ width: `${Math.max(1, value)}%` }} />
                  </div>
                  <span className="protocol-value">{value.toFixed(1)}%</span>
                </div>
              ))
            )}
          </div>
          {!loading && !hasProtocolData && (
            <div className="protocol-empty">No protocol data available</div>
          )}
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
                      <span className="talker-traffic">{bytes.toFixed(1)} MB}</span>
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
