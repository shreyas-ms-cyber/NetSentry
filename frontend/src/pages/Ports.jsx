import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getPorts } from '../services/api'
import './Ports.css'

const Ports = () => {
  const [loading, setLoading] = useState(true)
  const [ports, setPorts] = useState([])
  const [filteredPorts, setFilteredPorts] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [protocolFilter, setProtocolFilter] = useState('ALL')
  const [portFilter, setPortFilter] = useState('')

  useEffect(() => {
    fetchPorts()
  }, [])

  const fetchPorts = async () => {
    try {
      setLoading(true)
      const response = await getPorts()
      setPorts(response.data.ports || [])
      setFilteredPorts(response.data.ports || [])
    } catch (err) {
      console.error('Error fetching ports:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let result = [...ports]

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(p =>
        p.port.toString().includes(term) ||
        p.device_ip?.toLowerCase().includes(term)
      )
    }

    if (statusFilter !== 'ALL') {
      result = result.filter(p => p.status === statusFilter)
    }

    if (protocolFilter !== 'ALL') {
      result = result.filter(p => p.protocol === protocolFilter)
    }

    if (portFilter) {
      result = result.filter(p => p.port === parseInt(portFilter))
    }

    result.sort((a, b) => a.port - b.port)
    setFilteredPorts(result)
  }, [ports, searchTerm, statusFilter, protocolFilter, portFilter])

  const getStatusBadge = (status) => {
    if (status === 'OPEN') {
      return <span className="port-status-badge open">● OPEN</span>
    }
    if (status === 'CLOSED') {
      return <span className="port-status-badge closed">● CLOSED</span>
    }
    return <span className="port-status-badge filtered">● FILTERED</span>
  }

  const getStatusCount = (status) => {
    return ports.filter(p => p.status === status).length
  }

  const getProtocolCount = (protocol) => {
    return ports.filter(p => p.protocol === protocol).length
  }

  if (loading) {
    return (
      <div className="ports-page">
        <div className="ports-header">
          <h1 className="ports-title">Open Ports</h1>
          <p className="ports-subtitle">Loading port data...</p>
        </div>
        <div className="ports-skeleton">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="port-row-skeleton">
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
    <div className="ports-page">
      <div className="ports-header">
        <div>
          <h1 className="ports-title">Port Visibility</h1>
          <p className="ports-subtitle">
            {filteredPorts.length} ports · {getStatusCount('OPEN')} open · {getStatusCount('CLOSED')} closed · {getStatusCount('FILTERED')} filtered
          </p>
        </div>
        <button className="btn-refresh-ports" onClick={fetchPorts}>
          <FontAwesomeIcon icon="rotate" />
          Refresh
        </button>
      </div>

      <div className="ports-stats-summary">
        <div className="port-stat-card">
          <span className="stat-number">{getStatusCount('OPEN')}</span>
          <span className="stat-label">Open</span>
          <span className="stat-bar open" style={{ width: `${ports.length > 0 ? (getStatusCount('OPEN') / ports.length) * 100 : 0}%` }} />
        </div>
        <div className="port-stat-card">
          <span className="stat-number">{getStatusCount('CLOSED')}</span>
          <span className="stat-label">Closed</span>
          <span className="stat-bar closed" style={{ width: `${ports.length > 0 ? (getStatusCount('CLOSED') / ports.length) * 100 : 0}%` }} />
        </div>
        <div className="port-stat-card">
          <span className="stat-number">{getStatusCount('FILTERED')}</span>
          <span className="stat-label">Filtered</span>
          <span className="stat-bar filtered" style={{ width: `${ports.length > 0 ? (getStatusCount('FILTERED') / ports.length) * 100 : 0}%` }} />
        </div>
        <div className="port-stat-card">
          <span className="stat-number">{ports.length}</span>
          <span className="stat-label">Total Scanned</span>
          <span className="stat-bar total" style={{ width: '100%' }} />
        </div>
      </div>

      <div className="ports-controls">
        <div className="search-wrapper">
          <FontAwesomeIcon icon="magnifying-glass" className="search-icon" />
          <input
            type="text"
            className="search-input-ports"
            placeholder="Search by port or IP..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <button
            className={`filter-btn ${statusFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setStatusFilter('ALL')}
          >
            All ({ports.length})
          </button>
          <button
            className={`filter-btn open ${statusFilter === 'OPEN' ? 'active' : ''}`}
            onClick={() => setStatusFilter('OPEN')}
          >
            Open ({getStatusCount('OPEN')})
          </button>
          <button
            className={`filter-btn closed ${statusFilter === 'CLOSED' ? 'active' : ''}`}
            onClick={() => setStatusFilter('CLOSED')}
          >
            Closed ({getStatusCount('CLOSED')})
          </button>
          <button
            className={`filter-btn filtered ${statusFilter === 'FILTERED' ? 'active' : ''}`}
            onClick={() => setStatusFilter('FILTERED')}
          >
            Filtered ({getStatusCount('FILTERED')})
          </button>
        </div>

        <div className="port-controls-right">
          <select
            className="protocol-select"
            value={protocolFilter}
            onChange={(e) => setProtocolFilter(e.target.value)}
          >
            <option value="ALL">All Protocols</option>
            <option value="TCP">TCP ({getProtocolCount('TCP')})</option>
            <option value="UDP">UDP ({getProtocolCount('UDP')})</option>
          </select>

          <input
            type="number"
            className="port-filter-input"
            placeholder="Port #"
            value={portFilter}
            onChange={(e) => setPortFilter(e.target.value)}
          />
        </div>
      </div>

      <div className="ports-table-wrapper">
        <table className="ports-table">
          <thead>
            <tr>
              <th>Port</th>
              <th>Protocol</th>
              <th>Status</th>
              <th>Device</th>
              <th>IP Address</th>
              <th>Scanned At</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredPorts.length > 0 ? (
              filteredPorts.map((port) => (
                <tr key={port.id} className="port-row">
                  <td className="port-number mono">{port.port}</td>
                  <td className="port-protocol-cell">{port.protocol}</td>
                  <td>{getStatusBadge(port.status)}</td>
                  <td>{port.device_id || '—'}</td>
                  <td className="mono">{port.device_ip || '—'}</td>
                  <td className="mono">
                    {port.scanned_at ? new Date(port.scanned_at).toLocaleString() : '—'}
                  </td>
                  <td>
                    {port.device_id && (
                      <Link to={`/devices/${port.device_id}`} className="btn-view-device">
                        <FontAwesomeIcon icon="eye" />
                      </Link>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="ports-empty-state">
                  <div className="empty-icon">
                    <FontAwesomeIcon icon="plug" />
                  </div>
                  <p>No ports found</p>
                  <span>Try adjusting your filters or search terms</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Ports
