import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './SystemStatus.css'

const SystemStatus = () => {
  const [status, setStatus] = useState({
    backend: { status: 'operational', latency: '12ms' },
    database: { status: 'operational', latency: '8ms' },
    agent: { status: 'operational', lastHeartbeat: '12 seconds ago' },
    discovery: { status: 'operational', lastRun: '18 seconds ago' },
    traffic: { status: 'operational', lastUpdate: '7 seconds ago' },
    ingestion: { status: 'operational', lastIngest: '5 seconds ago' }
  })

  const getStatusBadge = (status) => {
    const map = {
      'operational': { class: 'status-operational', label: '● Operational' },
      'degraded': { class: 'status-degraded', label: '● Degraded' },
      'offline': { class: 'status-offline', label: '● Offline' }
    }
    const info = map[status] || map['offline']
    return <span className={`system-status-badge ${info.class}`}>{info.label}</span>
  }

  return (
    <div className="system-status-page">
      <div className="system-status-header">
        <h1 className="system-status-title">System Status</h1>
        <p className="system-status-subtitle">NetSentry infrastructure health monitoring</p>
      </div>

      <div className="system-status-grid">
        <div className="status-card">
          <div className="status-card-header">
            <span className="status-card-icon">
              <FontAwesomeIcon icon="server" />
            </span>
            <span className="status-card-name">Backend API</span>
          </div>
          <div className="status-card-body">
            {getStatusBadge(status.backend.status)}
            <span className="status-card-latency">Latency: {status.backend.latency}</span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-card-icon">
              <FontAwesomeIcon icon="database" />
            </span>
            <span className="status-card-name">Database</span>
          </div>
          <div className="status-card-body">
            {getStatusBadge(status.database.status)}
            <span className="status-card-latency">Latency: {status.database.latency}</span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-card-icon">
              <FontAwesomeIcon icon="satellite-dish" />
            </span>
            <span className="status-card-name">Local Agent</span>
          </div>
          <div className="status-card-body">
            {getStatusBadge(status.agent.status)}
            <span className="status-card-latency">Heartbeat: {status.agent.lastHeartbeat}</span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-card-icon">
              <FontAwesomeIcon icon="search" />
            </span>
            <span className="status-card-name">Device Discovery</span>
          </div>
          <div className="status-card-body">
            {getStatusBadge(status.discovery.status)}
            <span className="status-card-latency">Last run: {status.discovery.lastRun}</span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-card-icon">
              <FontAwesomeIcon icon="chart-line" />
            </span>
            <span className="status-card-name">Traffic Collection</span>
          </div>
          <div className="status-card-body">
            {getStatusBadge(status.traffic.status)}
            <span className="status-card-latency">Last update: {status.traffic.lastUpdate}</span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-card-icon">
              <FontAwesomeIcon icon="cloud-upload" />
            </span>
            <span className="status-card-name">Data Ingestion</span>
          </div>
          <div className="status-card-body">
            {getStatusBadge(status.ingestion.status)}
            <span className="status-card-latency">Last ingest: {status.ingestion.lastIngest}</span>
          </div>
        </div>
      </div>

      <div className="system-status-footer">
        <div className="status-legend">
          <span className="legend-item operational">● Operational</span>
          <span className="legend-item degraded">● Degraded</span>
          <span className="legend-item offline">● Offline</span>
        </div>
        <span className="status-updated">Last updated: Just now</span>
      </div>
    </div>
  )
}

export default SystemStatus
