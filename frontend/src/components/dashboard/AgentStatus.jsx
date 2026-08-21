import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './AgentStatus.css'

const AgentStatus = ({ status = 'online', lastHeartbeat, lastDiscovery, lastTraffic }) => {
  const isOnline = status === 'online'
  
  return (
    <div className={`agent-status-card ${isOnline ? 'online' : 'offline'}`}>
      <div className="agent-status-header">
        <div className="agent-status-indicator">
          <span className={`status-pulse ${isOnline ? 'online' : 'offline'}`}></span>
          <span className="agent-status-label">LOCAL AGENT</span>
        </div>
        <span className={`agent-status-text ${isOnline ? 'online' : 'offline'}`}>
          {isOnline ? '● ONLINE' : '● OFFLINE'}
        </span>
      </div>
      
      {isOnline ? (
        <div className="agent-status-details">
          <div className="agent-detail">
            <span className="agent-detail-label">Last heartbeat</span>
            <span className="agent-detail-value">{lastHeartbeat || 'Just now'}</span>
          </div>
          <div className="agent-detail">
            <span className="agent-detail-label">Last discovery</span>
            <span className="agent-detail-value">{lastDiscovery || 'Just now'}</span>
          </div>
          <div className="agent-detail">
            <span className="agent-detail-label">Last traffic update</span>
            <span className="agent-detail-value">{lastTraffic || 'Just now'}</span>
          </div>
        </div>
      ) : (
        <div className="agent-status-offline-msg">
          <p>Start the Local Agent to receive live network telemetry.</p>
        </div>
      )}
    </div>
  )
}

export default AgentStatus
