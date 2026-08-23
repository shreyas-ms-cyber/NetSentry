import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getDashboardSummary, getTraffic, getAlerts } from '../services/api'
import { getCached, setCached } from '../utils/cache'
import TrafficChart from '../components/dashboard/TrafficChart'
import ProtocolChart from '../components/dashboard/ProtocolChart'
import BandwidthChart from '../components/dashboard/BandwidthChart'
import TopTalkers from '../components/dashboard/TopTalkers'
import RecentEvents from '../components/dashboard/RecentEvents'
import './Dashboard.css'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(() => getCached('dashboard-summary'))
  const [trafficData, setTrafficData] = useState([]) // Always initialize as array
  const [alerts, setAlerts] = useState([]) // Always initialize as array
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAllData = async () => {
    try {
      setLoading(true)
      const [summaryRes, trafficRes, alertsRes] = await Promise.all([
        getDashboardSummary(),
        getTraffic({ limit: 50 }),
        getAlerts({ acknowledged: false })
      ])

      // SAFETY: Extract traffic array correctly
      let trafficArray = []
      if (trafficRes?.data) {
        if (Array.isArray(trafficRes.data)) {
          trafficArray = trafficRes.data
        } else if (trafficRes.data.traffic && Array.isArray(trafficRes.data.traffic)) {
          trafficArray = trafficRes.data.traffic
        }
      }

      // SAFETY: Extract alerts array correctly
      let alertsArray = []
      if (alertsRes?.data) {
        if (Array.isArray(alertsRes.data)) {
          alertsArray = alertsRes.data
        } else if (alertsRes.data.alerts && Array.isArray(alertsRes.data.alerts)) {
          alertsArray = alertsRes.data.alerts
        }
      }

      // Find the best entry (first with non-zero protocol breakdown)
      const bestTrafficEntry = trafficArray.find(entry => {
        const pb = entry.protocol_breakdown || {}
        return pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0
      }) || trafficArray[0] || null

      // Merge summary with the best traffic entry
      const mergedSummary = {
        ...summaryRes.data,
        latest_traffic: bestTrafficEntry || summaryRes.data?.latest_traffic
      }

      setSummary(mergedSummary)
      setTrafficData(trafficArray)
      setAlerts(alertsArray)
      setLastUpdated(new Date())

      // Cache data
      setCached('dashboard-summary', mergedSummary, 30)
      setCached('traffic-data', trafficArray, 30)
      setCached('alerts-data', alertsArray, 30)

    } catch (err) {
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  const stats = [
    { label: 'Total Devices', value: summary?.total_devices ?? '—', icon: 'server', color: '#00E5FF' },
    { label: 'Online Devices', value: summary?.online_devices ?? '—', icon: 'check-circle', color: '#00D26A' },
    { label: 'Offline Devices', value: summary?.offline_devices ?? '—', icon: 'power-off', color: '#FF3B5C' },
    { label: 'Open Ports', value: summary?.open_ports ?? '—', icon: 'plug', color: '#FFC857' },
    { label: 'Packets/sec', value: summary?.latest_traffic?.packets_per_sec?.toFixed(1) ?? '—', icon: 'arrow-up', color: '#4DA3FF' },
    { label: 'Bandwidth', value: summary?.latest_traffic?.bandwidth_mbps?.toFixed(1) ?? '—', icon: 'gauge-high', color: '#00D26A' },
  ]

  const protocolBreakdown = summary?.latest_traffic?.protocol_breakdown || {}
  const topTalkers = Array.isArray(summary?.latest_traffic?.top_talkers) ? summary.latest_traffic.top_talkers : []

  if (loading && !summary) {
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
          <TrafficChart data={trafficData} loading={loading} />
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="bottom-grid">
        <div className="chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Protocol Breakdown</div>
            <div className="chart-card-subtitle">Distribution</div>
          </div>
          <ProtocolChart data={summary?.latest_traffic || {}} loading={loading} />
        </div>

        <div className="chart-card">
          <div className="chart-card-header">
            <div className="chart-card-title">Top Talkers</div>
            <div className="chart-card-subtitle">Traffic volume</div>
          </div>
          <TopTalkers data={topTalkers} loading={loading} />
        </div>
      </div>

      {/* Recent Events */}
      <div className="chart-card full-width">
        <div className="chart-card-header">
          <div className="chart-card-title">Recent Network Events</div>
          <div className="chart-card-subtitle">Latest activity</div>
        </div>
        <RecentEvents alerts={alerts} loading={loading} />
      </div>
    </div>
  )
}

export default Dashboard
