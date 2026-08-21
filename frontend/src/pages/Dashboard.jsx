import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getDashboardSummary, getTraffic, getAlerts } from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [trafficData, setTrafficData] = useState([])
  const [alerts, setAlerts] = useState([])
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAllData = async () => {
    try {
      setLoading(true)
      const [summaryRes, trafficRes, alertsRes] = await Promise.all([
        getDashboardSummary(),
        getTraffic({ limit: 50 }),
        getAlerts({ acknowledged: false })
      ])
      setSummary(summaryRes.data)
      setTrafficData(trafficRes.data || [])
      setAlerts(alertsRes.data || [])
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  // If data is empty, refetch after 5 seconds (in case agent is still starting)
  useEffect(() => {
    if (!loading && summary && Object.keys(summary).length === 0) {
      const timer = setTimeout(() => fetchAllData(), 5000)
      return () => clearTimeout(timer)
    }
  }, [loading, summary])

  const stats = [
    { label: 'Total Devices', value: summary?.total_devices ?? '—', icon: 'server', color: '#00E5FF' },
    { label: 'Online Devices', value: summary?.online_devices ?? '—', icon: 'check-circle', color: '#00D26A' },
    { label: 'Offline Devices', value: summary?.offline_devices ?? '—', icon: 'power-off', color: '#FF3B5C' },
    { label: 'Open Ports', value: summary?.open_ports ?? '—', icon: 'plug', color: '#FFC857' },
    { label: 'Packets/sec', value: summary?.latest_traffic?.packets_per_sec?.toFixed(1) ?? '—', icon: 'arrow-up', color: '#4DA3FF' },
    { label: 'Bandwidth', value: summary?.latest_traffic?.bandwidth_mbps?.toFixed(1) ?? '—', icon: 'gauge-high', color: '#00D26A' },
  ]

  const protocolBreakdown = summary?.latest_traffic?.protocol_breakdown || {}
  const topTalkers = summary?.latest_traffic?.top_talkers || []

  // Show loading skeletons while fetching
  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Network Command Center</h1>
          <p className="dashboard-subtitle">Loading...</p>
        </div>
        <div className="stats-grid">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="stat-card skeleton" style={{ height: '100px' }} />
          ))}
        </div>
        <div className="chart-card skeleton" style={{ height: '250px' }} />
      </div>
    )
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-header-left">
          <h1 className="dashboard-title">Network Command Center</h1>
          <p className="dashboard-subtitle">Real-time visibility across your authorized network</p>
        </div>
        <div className="dashboard-header-right">
          <div className="agent-health">
            <span className="status-dot online pulse"></span>
            <span className="agent-label">AGENT ONLINE</span>
            <span className="agent-time">Last sync {lastUpdated ? `${Math.floor((Date.now() - lastUpdated.getTime()) / 1000)}s ago` : '—'}</span>
          </div>
          <button className="btn-refresh" onClick={fetchAllData}>
            <FontAwesomeIcon icon="rotate" />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-card-header">
              <span className="stat-card-label">{stat.label}</span>
              <FontAwesomeIcon icon={stat.icon} className="stat-card-icon" style={{ color: stat.color }} />
            </div>
            <div className="stat-card-value" style={{ color: stat.color }}>{stat.value}</div>
            <div className="stat-card-trend">
              <span className="trend-indicator">●</span>
              <span className="trend-label">Live</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        <div className="chart-card full-width">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Network Traffic</div>
              <div className="chart-card-subtitle">Packets per second over time</div>
            </div>
            <div className="chart-card-actions">
              <button className="time-btn active">1H</button>
              <button className="time-btn">6H</button>
              <button className="time-btn">24H</button>
              <button className="time-btn">7D</button>
            </div>
          </div>
          <div className="chart-placeholder">
            <div className="chart-metric">
              <span className="metric-value">{summary?.latest_traffic?.packets_per_sec?.toFixed(0) || '—'}</span>
              <span className="metric-label">Current pps</span>
            </div>
            <div className="chart-area">
              {trafficData.length > 0 ? (
                <div className="chart-bars">
                  {trafficData.slice(0, 30).reverse().map((d, i) => (
                    <div
                      key={i}
                      className="chart-bar"
                      style={{
                        height: `${Math.min((d.packets_per_sec || 0) / (Math.max(...trafficData.map(t => t.packets_per_sec || 0)) || 1) * 80 + 10, 90)}%`,
                        backgroundColor: `rgba(0, 229, 255, ${0.2 + (d.packets_per_sec || 0) / (Math.max(...trafficData.map(t => t.packets_per_sec || 0)) || 1) * 0.6})`
                      }}
                    />
                  ))}
                </div>
              ) : (
                <div className="chart-empty">
                  <p>No traffic data available</p>
                  <span>Start the Local Agent to begin monitoring</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="bottom-grid">
        <div className="chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Protocol Breakdown</div>
            <div className="chart-card-subtitle">Distribution</div>
          </div>
          <div className="protocol-breakdown">
            {Object.keys(protocolBreakdown).length > 0 ? (
              Object.entries(protocolBreakdown).map(([proto, value]) => (
                <div key={proto} className="protocol-item">
                  <span className="protocol-name">{proto.toUpperCase()}</span>
                  <div className="protocol-bar-track">
                    <div className="protocol-bar-fill" style={{ width: `${value}%` }} />
                  </div>
                  <span className="protocol-value">{value.toFixed(1)}%</span>
                </div>
              ))
            ) : (
              <div className="protocol-empty">No protocol data</div>
            )}
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Top Talkers</div>
            <div className="chart-card-subtitle">Traffic volume</div>
          </div>
          <div className="top-talkers">
            {topTalkers.length > 0 ? (
              topTalkers.slice(0, 5).map((talker, i) => (
                <div key={i} className="talker-item">
                  <div className="talker-info">
                    <span className="talker-ip">{talker.ip}</span>
                    <span className="talker-traffic">{talker.bytes_mb?.toFixed(1) || '0'} MB</span>
                  </div>
                  <div className="talker-bar-track">
                    <div className="talker-bar-fill" style={{ width: `${Math.min((talker.bytes_mb || 0) / (topTalkers[0]?.bytes_mb || 1) * 100, 100)}%` }} />
                  </div>
                </div>
              ))
            ) : (
              <div className="talkers-empty">No traffic data available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
