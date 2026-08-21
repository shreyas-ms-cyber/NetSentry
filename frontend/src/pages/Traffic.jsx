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
      const data = response.data || []
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

      {/* Charts */}
      <div className="traffic-charts">
        <div className="traffic-chart-card full-width">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Traffic Timeline</div>
              <div className="chart-card-subtitle">Packets per second over time</div>
            </div>
          </div>
          <TrafficChart data={trafficData} loading={loading} />
        </div>

        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Bandwidth</div>
              <div className="chart-card-subtitle">Mbps over time</div>
            </div>
          </div>
          <BandwidthChart data={trafficData} loading={loading} />
        </div>

        <div className="traffic-chart-card">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Protocol Distribution</div>
              <div className="chart-card-subtitle">Current breakdown</div>
            </div>
          </div>
          <ProtocolChart data={latestTraffic || {}} loading={loading} />
        </div>

        <div className="traffic-chart-card full-width">
          <div className="chart-card-header">
            <div>
              <div className="chart-card-title">Top Talkers</div>
              <div className="chart-card-subtitle">Devices by traffic volume</div>
            </div>
          </div>
          <TopTalkers data={latestTraffic?.top_talkers || []} loading={loading} />
        </div>
      </div>
    </div>
  )
}

export default Traffic
