import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './RecentEvents.css'

const RecentEvents = ({ alerts, loading }) => {
  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'HIGH': return '#FF3B5C'
      case 'MEDIUM': return '#FFC857'
      case 'LOW': return '#00D26A'
      default: return 'rgba(255,255,255,0.3)'
    }
  }

  const getAlertIcon = (type) => {
    switch (type) {
      case 'NEW_DEVICE': return 'plus-circle'
      case 'NEW_OPEN_PORT': return 'plug'
      case 'DEVICE_OFFLINE': return 'power-off'
      case 'DEVICE_ONLINE': return 'check-circle'
      default: return 'circle'
    }
  }

  if (loading) {
    return (
      <div className="recent-events">
        {[1, 2, 3].map(i => (
          <div key={i} className="event-item skeleton" style={{ height: '52px' }}></div>
        ))}
      </div>
    )
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="recent-events empty">
        <p style={{ color: 'rgba(255,255,255,0.2)', textAlign: 'center', padding: '16px 0' }}>
          No recent network events
        </p>
      </div>
    )
  }

  const getTimeAgo = (timestamp) => {
    if (!timestamp) return 'Just now'
    const diff = Date.now() - new Date(timestamp).getTime()
    const minutes = Math.floor(diff / 60000)
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes} min ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
    const days = Math.floor(hours / 24)
    return `${days} day${days > 1 ? 's' : ''} ago`
  }

  return (
    <div className="recent-events">
      {alerts.slice(0, 5).map((alert) => (
        <div key={alert.id} className="event-item">
          <div className="event-icon" style={{ color: getSeverityColor(alert.severity) }}>
            <FontAwesomeIcon icon={getAlertIcon(alert.alert_type)} />
          </div>
          <div className="event-content">
            <div className="event-description">{alert.description}</div>
            <div className="event-meta">
              <span className="event-severity" style={{ color: getSeverityColor(alert.severity) }}>
                {alert.severity || 'INFO'}
              </span>
              <span className="event-time">{getTimeAgo(alert.timestamp)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default RecentEvents
