import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getTraffic } from '../services/api'
import './Traffic.css'

const Traffic = () => {
  const [loading, setLoading] = useState(true)
  const [trafficData, setTrafficData] = useState([])
  const [latestTraffic, setLatestTraffic] = useState(null)
  const [stats, setStats] = useState({
    totalPackets: 0,
    avgPps: 0,
    peakPps: 0,
    totalBandwidth: 0
  })

  const fetchTraffic = async () => {
    try {
      setLoading(true)
      const response = await getTraffic({ limit: 100 })
      // Ensure data is always an array
      const data = Array.isArray(response.data) ? response.data : []
      setTrafficData(data)
      
      if (data.length > 0) {
        setLatestTraffic(data[0])
        const ppsValues = data.map(d => d.packets_per_sec || 0)
        setStats({
          totalPackets: data.reduce((sum, d) => sum + (d.total_packets || 0), 0),
          avgPps: ppsValues.reduce((a, b) => a + b, 0) / ppsValues.length,
          peakPps: Math.max(...ppsValues),
          totalBandwidth: data.reduce((sum, d) => sum + (d.bandwidth_bytes || 0), 0)
        })
      }
    } catch (err) {
      console.error('Error fetching traffic:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTraffic()
  }, [])

  // Safe function to get protocol breakdown with fallback
  const getProtocolBreakdown = () => {
    if (!latestTraffic) return {}
    const breakdown = latestTraffic.protocol_breakdown || {}
    // Ensure we have all protocol keys
    return {
      tcp: breakdown.tcp || 0,
      udp: breakdown.udp || 0,
      icmp: breakdown.icmp || 0,
      other: breakdown.other || 0
    }
  }

  // Safe function to get top talkers with fallback
  const getTopTalkers = () => {
    if (!latestTraffic) return []
    return Array.isArray(latestTraffic.top_talkers) ? latestTraffic.top_talkers : []
  }

  // Show loading state
  if (loading) {
    return (
      <div className="traffic-page">
        <div className="traffic-header">
          <div>
            <h1 className="traffic-title">Network Traffic</h1>
            <p className="traffic-subtitle">Loading traffic data...</p>
          </div>
        </div>
        <div className="traffic-stats">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="traffic-stat-card skeleton" style={{ height: '80px' }} />
          ))}
        </div>
        <div className="traffic-charts">
          <div className="traffic-chart-card full-width skeleton" style={{ height: '250px' }} />
          <div className="traffic-chart-card skeleton" style={{ height: '200px' }} />
          <div className="traffic-chart-card skeleton" style={{ height: '200px' }} />
        </div>
      </div>
    )
  }

  const protocolBreakdown = getProtocolBreakdown()
  const topTalkers = getTopTalkers()
  const hasProtocolData = Object.values(protocolBreakdown).some(v => v > 0)

  return (
    <div className="traffic-page">
      {/* Header */}
      <div className="traffic-header">
        <div>
          <h1 className="traffic-title">Network Traffic</h1>
          <p className="traffic-subtitle">Real-time network traffic analysis</p>
        </div>
        <button className="btn-refresh-traffic" onClick={fetchTraffic}>
          <FontAwesomeIcon icon="rotate" />
          Refresh
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
      <div className="traffic-charts">
        <div className="traffic-chart-card full-width">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Traffic Timeline</div>
              <div className="chart-card-subtitle">Packets per second over time</div>
            </div>
          </div>
          <div className="chart-container">
            {trafficData.length > 0 ? (
              <div className="chart-bars-wrapper">
                {trafficData.slice(0, 50).reverse().map((d, i) => {
                  const maxPps = Math.max(...trafficData.map(t => t.packets_per_sec || 0), 1)
                  const height = Math.max(5, ((d.packets_per_sec || 0) / maxPps) * 100)
                  return (
                    <div key={i} className="chart-bar-item">
                      <div 
                        className="chart-bar-fill" 
                        style={{ 
                          height: `${height}%`,
                          backgroundColor: `rgba(0, 229, 255, ${0.3 + (height / 100) * 0.6})`
                        }}
                      />
                      <span className="chart-bar-label">
                        {new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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

        {/* Protocol Distribution */}
        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Protocol Distribution</div>
              <div className="chart-card-subtitle">Current breakdown</div>
            </div>
          </div>
          <div className="protocol-list">
            {hasProtocolData ? (
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
            <div>
              <div className="chart-card-title">Top Talkers</div>
              <div className="chart-card-subtitle">Devices by traffic volume</div>
            </div>
          </div>
          <div className="talkers-list">
            {topTalkers.length > 0 ? (
              topTalkers.slice(0, 5).map((talker, i) => {
                const maxBytes = topTalkers[0]?.bytes_mb || 1
                return (
                  <div key={i} className="talker-item">
                    <div className="talker-info">
                      <span className="talker-ip">{talker.ip || 'Unknown'}</span>
                      <span className="talker-traffic">{talker.bytes_mb?.toFixed(1) || '0'} MB</span>
                    </div>
                    <div className="talker-bar-track">
                      <div 
                        className="talker-bar-fill" 
                        style={{ 
                          width: `${Math.min((talker.bytes_mb || 0) / maxBytes * 100, 100)}%` 
                        }} 
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
