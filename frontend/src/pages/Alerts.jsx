import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getAlerts, acknowledgeAlert } from '../services/api'
import './Alerts.css'

const Alerts = () => {
  const [loading, setLoading] = useState(true)
  const [alerts, setAlerts] = useState([])
  const [filteredAlerts, setFilteredAlerts] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [severityFilter, setSeverityFilter] = useState('ALL')
  const [ackFilter, setAckFilter] = useState('ALL')
  const [acknowledging, setAcknowledging] = useState(null)

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const response = await getAlerts()
      // SAFE: Always ensure we have an array
      const alertsData = response?.data?.alerts || []
      setAlerts(Array.isArray(alertsData) ? alertsData : [])
      setFilteredAlerts(Array.isArray(alertsData) ? alertsData : [])
    } catch (err) {
      console.error('Error fetching alerts:', err)
      setAlerts([])
      setFilteredAlerts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let result = Array.isArray(alerts) ? [...alerts] : []

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(a =>
        a.description?.toLowerCase().includes(term) ||
        a.alert_type?.toLowerCase().includes(term) ||
        a.device_ip?.toLowerCase().includes(term)
      )
    }

    if (severityFilter !== 'ALL') {
      result = result.filter(a => a.severity === severityFilter)
    }

    if (ackFilter === 'ACKNOWLEDGED') {
      result = result.filter(a => a.acknowledged === true)
    } else if (ackFilter === 'UNACKNOWLEDGED') {
      result = result.filter(a => a.acknowledged === false)
    }

    result.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    setFilteredAlerts(result)
  }, [alerts, searchTerm, severityFilter, ackFilter])

  const handleAcknowledge = async (id) => {
    try {
      setAcknowledging(id)
      await acknowledgeAlert(id)
      await fetchAlerts()
    } catch (err) {
      console.error('Error acknowledging alert:', err)
    } finally {
      setAcknowledging(null)
    }
  }

  const getSeverityBadge = (severity) => {
    const map = {
      'HIGH': { class: 'high', icon: 'exclamation-triangle' },
      'MEDIUM': { class: 'medium', icon: 'exclamation-circle' },
      'LOW': { class: 'low', icon: 'info-circle' }
    }
    const info = map[severity] || { class: 'info', icon: 'circle' }
    return <span className={`severity-badge ${info.class}`}>{severity || 'INFO'}</span>
  }

  const getAlertIcon = (type) => {
    const map = {
      'NEW_DEVICE': 'plus-circle',
      'NEW_OPEN_PORT': 'plug',
      'DEVICE_OFFLINE': 'power-off',
      'DEVICE_ONLINE': 'check-circle'
    }
    return map[type] || 'circle'
  }

  const getAlertLabel = (type) => {
    const map = {
      'NEW_DEVICE': 'New Device',
      'NEW_OPEN_PORT': 'New Open Port',
      'DEVICE_OFFLINE': 'Device Offline',
      'DEVICE_ONLINE': 'Device Online'
    }
    return map[type] || type
  }

  const getSeverityCount = (severity) => {
    const alertsArray = Array.isArray(alerts) ? alerts : []
    return alertsArray.filter(a => a.severity === severity).length
  }

  const getUnacknowledgedCount = () => {
    const alertsArray = Array.isArray(alerts) ? alerts : []
    return alertsArray.filter(a => !a.acknowledged).length
  }

  if (loading) {
    return (
      <div className="alerts-page">
        <div className="alerts-header">
          <h1 className="alerts-title">Security Alerts</h1>
          <p className="alerts-subtitle">Loading alerts...</p>
        </div>
        <div className="alerts-skeleton">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="alert-skeleton">
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const alertsArray = Array.isArray(filteredAlerts) ? filteredAlerts : []
  const totalAlerts = alertsArray.length

  return (
    <div className="alerts-page">
      <div className="alerts-header">
        <div>
          <h1 className="alerts-title">Security Alerts</h1>
          <p className="alerts-subtitle">
            {totalAlerts} alerts · {getUnacknowledgedCount()} unacknowledged
          </p>
        </div>
        <button className="btn-refresh-alerts" onClick={fetchAlerts}>
          <FontAwesomeIcon icon="rotate" />
          Refresh
        </button>
      </div>

      <div className="alerts-summary">
        <div className="alert-summary-card high">
          <span className="summary-number">{getSeverityCount('HIGH')}</span>
          <span className="summary-label">Critical</span>
        </div>
        <div className="alert-summary-card medium">
          <span className="summary-number">{getSeverityCount('MEDIUM')}</span>
          <span className="summary-label">High</span>
        </div>
        <div className="alert-summary-card low">
          <span className="summary-number">{getSeverityCount('LOW')}</span>
          <span className="summary-label">Medium</span>
        </div>
        <div className="alert-summary-card info">
          <span className="summary-number">{getUnacknowledgedCount()}</span>
          <span className="summary-label">Unacknowledged</span>
        </div>
      </div>

      <div className="alerts-controls">
        <div className="search-wrapper">
          <FontAwesomeIcon icon="magnifying-glass" className="search-icon" />
          <input
            type="text"
            className="search-input-alerts"
            placeholder="Search alerts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <button
            className={`filter-btn ${severityFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('ALL')}
          >
            All ({totalAlerts})
          </button>
          <button
            className={`filter-btn high ${severityFilter === 'HIGH' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('HIGH')}
          >
            Critical ({getSeverityCount('HIGH')})
          </button>
          <button
            className={`filter-btn medium ${severityFilter === 'MEDIUM' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('MEDIUM')}
          >
            High ({getSeverityCount('MEDIUM')})
          </button>
          <button
            className={`filter-btn low ${severityFilter === 'LOW' ? 'active' : ''}`}
            onClick={() => setSeverityFilter('LOW')}
          >
            Medium ({getSeverityCount('LOW')})
          </button>
        </div>

        <select
          className="ack-filter"
          value={ackFilter}
          onChange={(e) => setAckFilter(e.target.value)}
        >
          <option value="ALL">All Status</option>
          <option value="UNACKNOWLEDGED">Unacknowledged</option>
          <option value="ACKNOWLEDGED">Acknowledged</option>
        </select>
      </div>

      <div className="alerts-list">
        {totalAlerts > 0 ? (
          alertsArray.map((alert) => (
            <div key={alert.id} className={`alert-item ${alert.acknowledged ? 'acknowledged' : ''}`}>
              <div className="alert-icon">
                <FontAwesomeIcon icon={getAlertIcon(alert.alert_type)} />
              </div>
              <div className="alert-content">
                <div className="alert-header">
                  <span className="alert-type">{getAlertLabel(alert.alert_type)}</span>
                  {getSeverityBadge(alert.severity)}
                  {alert.acknowledged && (
                    <span className="ack-badge">Acknowledged</span>
                  )}
                </div>
                <p className="alert-description">{alert.description}</p>
                <div className="alert-meta">
                  <span className="alert-device">
                    {alert.device_ip && (
                      <Link to={`/devices/${alert.device_id}`} className="alert-device-link">
                        <FontAwesomeIcon icon="network-wired" />
                        {alert.device_ip}
                      </Link>
                    )}
                  </span>
                  <span className="alert-time">
                    <FontAwesomeIcon icon="clock" />
                    {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : '—'}
                  </span>
                </div>
              </div>
              <div className="alert-actions">
                {!alert.acknowledged && (
                  <button
                    className="btn-acknowledge"
                    onClick={() => handleAcknowledge(alert.id)}
                    disabled={acknowledging === alert.id}
                  >
                    {acknowledging === alert.id ? (
                      <FontAwesomeIcon icon="spinner" spin />
                    ) : (
                      'Acknowledge'
                    )}
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="alerts-empty">
            <div className="empty-icon">
              <FontAwesomeIcon icon="shield" />
            </div>
            <p>No alerts found</p>
            <span>All clear! No security alerts to display</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default Alerts
