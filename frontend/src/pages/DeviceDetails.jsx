import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getDevice, getDevicePorts } from '../services/api'
import './DeviceDetails.css'

const DeviceDetails = () => {
  const { id } = useParams()
  const [loading, setLoading] = useState(true)
  const [device, setDevice] = useState(null)
  const [ports, setPorts] = useState([])

  useEffect(() => {
    fetchDeviceDetails()
  }, [id])

  const fetchDeviceDetails = async () => {
    try {
      setLoading(true)
      const [deviceRes, portsRes] = await Promise.all([
        getDevice(id),
        getDevicePorts(id)
      ])
      setDevice(deviceRes.data)
      setPorts(portsRes.data.ports || [])
    } catch (err) {
      console.error('Error fetching device details:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    if (status === 'ONLINE') {
      return <span className="detail-status online"><span className="status-dot pulse"></span> Online</span>
    }
    return <span className="detail-status offline"><span className="status-dot"></span> Offline</span>
  }

  const getPortStatusBadge = (status) => {
    if (status === 'OPEN') {
      return <span className="port-badge open">● Open</span>
    }
    if (status === 'CLOSED') {
      return <span className="port-badge closed">● Closed</span>
    }
    return <span className="port-badge filtered">● Filtered</span>
  }

  if (loading) {
    return (
      <div className="device-detail-page">
        <div className="detail-skeleton">
          <div className="skeleton-header"></div>
          <div className="skeleton-info"></div>
          <div className="skeleton-ports"></div>
        </div>
      </div>
    )
  }

  if (!device) {
    return (
      <div className="device-detail-page">
        <div className="detail-empty">
          <FontAwesomeIcon icon="triangle-exclamation" />
          <p>Device not found</p>
          <Link to="/devices">Return to Devices</Link>
        </div>
      </div>
    )
  }

  const openPorts = ports.filter(p => p.status === 'OPEN')
  const closedPorts = ports.filter(p => p.status === 'CLOSED')
  const filteredPorts = ports.filter(p => p.status === 'FILTERED')

  return (
    <div className="device-detail-page">
      {/* Back Button */}
      <Link to="/devices" className="back-link">
        <FontAwesomeIcon icon="arrow-left" />
        Back to Devices
      </Link>

      {/* Header */}
      <div className="detail-header">
        <div className="detail-header-left">
          <h1 className="detail-title">{device.ip_address}</h1>
          <div className="detail-meta">
            {getStatusBadge(device.status)}
            <span className="detail-vendor">{device.vendor || 'Unknown Vendor'}</span>
          </div>
        </div>
        <button className="btn-refresh-detail" onClick={fetchDeviceDetails}>
          <FontAwesomeIcon icon="rotate" />
          Refresh
        </button>
      </div>

      {/* Info Grid */}
      <div className="detail-info-grid">
        <div className="info-item">
          <span className="info-label">IP Address</span>
          <span className="info-value mono">{device.ip_address}</span>
        </div>
        <div className="info-item">
          <span className="info-label">MAC Address</span>
          <span className="info-value mono">{device.mac_address}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Hostname</span>
          <span className="info-value">{device.hostname || '—'}</span>
        </div>
        <div className="info-item">
          <span className="info-label">First Seen</span>
          <span className="info-value mono">
            {device.first_seen ? new Date(device.first_seen).toLocaleString() : '—'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Last Seen</span>
          <span className="info-value mono">
            {device.last_seen ? new Date(device.last_seen).toLocaleString() : '—'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Open Ports</span>
          <span className="info-value port-count-large">{openPorts.length}</span>
        </div>
      </div>

      {/* Ports Section */}
      <div className="detail-ports-section">
        <div className="ports-header">
          <h2 className="ports-title">Open Ports</h2>
          <div className="ports-stats">
            <span className="port-stat open">{openPorts.length} Open</span>
            <span className="port-stat closed">{closedPorts.length} Closed</span>
            <span className="port-stat filtered">{filteredPorts.length} Filtered</span>
          </div>
        </div>

        {ports.length > 0 ? (
          <div className="ports-grid">
            {ports.map((port) => (
              <div key={port.id} className="port-card">
                <div className="port-number mono">{port.port}</div>
                <div className="port-protocol">{port.protocol}</div>
                {getPortStatusBadge(port.status)}
                <div className="port-time mono">
                  {port.scanned_at ? new Date(port.scanned_at).toLocaleString() : '—'}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="ports-empty">
            <p>No port scan data available for this device</p>
            <span>Run the Local Agent to discover open ports</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default DeviceDetails
