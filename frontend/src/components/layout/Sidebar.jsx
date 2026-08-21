import React from 'react'
import { NavLink } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './Sidebar.css'

const Sidebar = ({ collapsed, onToggle }) => {
  const navItems = [
    { path: '/', icon: 'gauge-high', label: 'Dashboard', section: 'MONITOR' },
    { path: '/devices', icon: 'network-wired', label: 'Devices', section: 'MONITOR' },
    { path: '/ports', icon: 'plug', label: 'Ports', section: 'MONITOR' },
    { path: '/traffic', icon: 'chart-line', label: 'Traffic', section: 'MONITOR' },
    { path: '/alerts', icon: 'triangle-exclamation', label: 'Alerts', section: 'SECURITY' },
    { path: '/system-status', icon: 'server', label: 'System Status', section: 'SYSTEM' },
    { path: '/about', icon: 'circle-info', label: 'About', section: 'SYSTEM' },
  ]

  const sections = {}
  navItems.forEach(item => {
    if (!sections[item.section]) sections[item.section] = []
    sections[item.section].push(item)
  })

  const isMobile = window.innerWidth < 768

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${isMobile ? 'mobile' : ''}`}>
      <div className="sidebar-brand">
        <div className="brand-icon">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <rect x="2" y="2" width="32" height="32" rx="8" stroke="#00E5FF" strokeWidth="2"/>
            <path d="M12 12L24 24M12 24L24 12" stroke="#00E5FF" strokeWidth="2" strokeLinecap="round"/>
            <circle cx="18" cy="18" r="5" stroke="#00E5FF" strokeWidth="2"/>
            <circle cx="18" cy="18" r="2" fill="#00E5FF"/>
          </svg>
        </div>
        {!collapsed && (
          <div className="brand-text">
            <span className="brand-name">NetSentry</span>
            <span className="brand-sub">Network Monitoring</span>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        {Object.keys(sections).map(section => (
          <div key={section} className="nav-section">
            {!collapsed && <div className="nav-section-label">{section}</div>}
            {sections[section].map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                onClick={onToggle}
              >
                <FontAwesomeIcon icon={item.icon} className="nav-icon" />
                {!collapsed && <span className="nav-label">{item.label}</span>}
                {collapsed && <span className="nav-tooltip">{item.label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-version">v1.0.0</div>
        {!isMobile && (
          <button className="sidebar-toggle" onClick={onToggle}>
            <FontAwesomeIcon icon={collapsed ? 'chevron-right' : 'chevron-left'} />
          </button>
        )}
      </div>
    </aside>
  )
}

export default Sidebar
