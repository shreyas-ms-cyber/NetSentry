import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './Topbar.css'

const Topbar = ({ onMenuClick, isMobile }) => {
  const [agentStatus, setAgentStatus] = useState('online')

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1 className="page-title">
          {isMobile ? 'NetSentry' : 'Network Command Center'}
        </h1>
        {!isMobile && (
          <span className="page-subtitle">Real-time visibility across your authorized network</span>
        )}
      </div>

      <div className="topbar-right">
        <div className="agent-status">
          <span className={`status-dot ${agentStatus} pulse`}></span>
          <span className="status-label">Agent {agentStatus}</span>
          {!isMobile && (
            <>
              <span className="status-divider">•</span>
              <span className="status-time">Last sync 12s ago</span>
            </>
          )}
        </div>

        {!isMobile && (
          <div className="search-container">
            <FontAwesomeIcon icon="magnifying-glass" className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search IP, MAC, hostname, port..."
            />
            <kbd className="search-shortcut">⌘K</kbd>
          </div>
        )}

        <button className="notif-btn" aria-label="Notifications">
          <FontAwesomeIcon icon="bell" />
          <span className="notif-badge">3</span>
        </button>

        <button className="refresh-btn" aria-label="Refresh">
          <FontAwesomeIcon icon="rotate" />
        </button>
      </div>
    </header>
  )
}

export default Topbar
