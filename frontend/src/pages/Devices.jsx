import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getDevices } from '../services/api'
import './Devices.css'

const Devices = () => {
  const [loading, setLoading] = useState(true)
  const [devices, setDevices] = useState([])
  const [filteredDevices, setFilteredDevices] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [sortBy, setSortBy] = useState('lastSeen')

  useEffect(() => {
    fetchDevices()
  }, [])

  const fetchDevices = async () => {
    try {
      setLoading(true)
      const response = await getDevices()
      setDevices(response.data.devices || [])
      setFilteredDevices(response.data.devices || [])
    } catch (err) {
      console.error('Error fetching devices:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let result = [...devices]

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(d =>
        d.ip_address?.toLowerCase().includes(term) ||
        d.hostname?.toLowerCase().includes(term) ||
        d.mac_address?.toLowerCase().includes(term) ||
        d.vendor?.toLowerCase().includes(term)
      )
    }

    // Status filter
    if (statusFilter !== 'ALL') {
      result = result.filter(d => d.status === statusFilter)
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'lastSeen') {
        return new Date(b.last_seen) - new Date(a.last_seen)
      }
      if (sortBy === 'firstSeen') {
        return new Date(b.first_seen) - new Date(a.first_seen)
      }
      if (sortBy === 'ip') {
        return a.ip_address.localeCompare(b.ip_address)
      }
      return 0
    })

    setFilteredDevices(result)
  }, [devices, searchTerm, statusFilter, sortBy])

  const getStatusBadge = (status) => {
    if (status === 'ONLINE') {
      return <span className="device-status online"><span className="status-dot pulse"></span> Online</span>
    }
    return <span className="device-status offline"><span className="status-dot"></span> Offline</span>
  }

  const getStatusCount = (status) => {
    return devices.filter(d => d.status === status).length
  }

  if (loading) {
    return (
      <div className="devices-page">
        <div className="devices-header">
          <h1 className="devices-title">Active Devices</h1>
          <p className="devices-subtitle">Loading devices...</p>
        </div>
        <div className="devices-skeleton">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="device-row-skeleton">
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="devices-page">
      {/* Header */}
      <div className="devices-header">
        <div>
          <h1 className="devices-title">Active Devices</h1>
          <p className="devices-subtitle">
            {filteredDevices.length} devices · {getStatusCount('ONLINE')} online · {getStatusCount('OFFLINE')} offline
          </p>
        </div>
        <button className="btn-refresh-devices" onClick={fetchDevices}>
          <FontAwesomeIcon icon="rotate" />
          Refresh
        </button>
      </div>

      {/* Controls */}
      <div className="devices-controls">
        <div className="search-wrapper">
          <FontAwesomeIcon icon="magnifying-glass" className="search-icon" />
          <input
            type="text"
            className="search-input-devices"
            placeholder="Search by IP, MAC, hostname, vendor..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <button
            className={`filter-btn ${statusFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setStatusFilter('ALL')}
          >
            All ({devices.length})
          </button>
          <button
            className={`filter-btn online ${statusFilter === 'ONLINE' ? 'active' : ''}`}
            onClick={() => setStatusFilter('ONLINE')}
          >
            <span className="status-dot pulse"></span>
            Online ({getStatusCount('ONLINE')})
          </button>
          <button
            className={`filter-btn offline ${statusFilter === 'OFFLINE' ? 'active' : ''}`}
            onClick={() => setStatusFilter('OFFLINE')}
          >
            <span className="status-dot"></span>
            Offline ({getStatusCount('OFFLINE')})
          </button>
        </div>

        <div className="sort-group">
          <label>Sort by</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="lastSeen">Last Seen</option>
            <option value="firstSeen">First Seen</option>
            <option value="ip">IP Address</option>
          </select>
        </div>
      </div>

      {/* Device Table - Desktop */}
      <div className="devices-table-wrapper">
        <table className="devices-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>IP Address</th>
              <th>MAC Address</th>
              <th>Hostname</th>
              <th>Vendor</th>
              <th>Last Seen</th>
              <th>Ports</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredDevices.length > 0 ? (
              filteredDevices.map((device) => (
                <tr key={device.id} className="device-row">
                  <td>{getStatusBadge(device.status)}</td>
                  <td className="mono">{device.ip_address}</td>
                  <td className="mono">{device.mac_address}</td>
                  <td>{device.hostname || '—'}</td>
                  <td>{device.vendor || 'Unknown'}</td>
                  <td className="mono">
                    {device.last_seen ? new Date(device.last_seen).toLocaleString() : '—'}
                  </td>
                  <td>
                    <span className="port-count">{device.open_ports_count || 0}</span>
                  </td>
                  <td>
                    <Link to={`/devices/${device.id}`} className="btn-detail">
                      View
                      <FontAwesomeIcon icon="chevron-right" className="btn-icon" />
                    </Link>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" className="empty-state">
                  <div className="empty-icon">
                    <FontAwesomeIcon icon="network-wired" />
                  </div>
                  <p>No devices found</p>
                  <span>Try adjusting your filters or search terms</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Device Cards - Mobile */}
      <div className="device-cards">
        {filteredDevices.map((device) => (
          <div key={device.id} className="device-card">
            <div className="device-card-header">
              {getStatusBadge(device.status)}
              <span className="device-card-ip mono">{device.ip_address}</span>
            </div>
            <div className="device-card-body">
              <div className="device-card-detail">
                <span className="label">MAC</span>
                <span className="value mono">{device.mac_address}</span>
              </div>
              <div className="device-card-detail">
                <span className="label">Hostname</span>
                <span className="value">{device.hostname || '—'}</span>
              </div>
              <div className="device-card-detail">
                <span className="label">Vendor</span>
                <span className="value">{device.vendor || 'Unknown'}</span>
              </div>
              <div className="device-card-detail">
                <span className="label">Last Seen</span>
                <span className="value mono">
                  {device.last_seen ? new Date(device.last_seen).toLocaleString() : '—'}
                </span>
              </div>
              <div className="device-card-detail">
                <span className="label">Open Ports</span>
                <span className="value port-count">{device.open_ports_count || 0}</span>
              </div>
            </div>
            <Link to={`/devices/${device.id}`} className="device-card-action">
              View Details
              <FontAwesomeIcon icon="arrow-right" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Devices
