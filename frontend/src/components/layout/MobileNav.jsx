import React from 'react'
import { NavLink } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './MobileNav.css'

const MobileNav = ({ onMenuClick }) => {
  const navItems = [
    { path: '/', icon: 'gauge-high', label: 'Dashboard' },
    { path: '/devices', icon: 'network-wired', label: 'Devices' },
    { path: '/traffic', icon: 'chart-line', label: 'Traffic' },
    { path: '/alerts', icon: 'triangle-exclamation', label: 'Alerts' },
  ]

  return (
    <nav className="mobile-nav">
      {/* Main nav items */}
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}
        >
          <FontAwesomeIcon icon={item.icon} className="mobile-nav-icon" />
          <span className="mobile-nav-label">{item.label}</span>
        </NavLink>
      ))}
      
      {/* Hamburger menu button - opens sidebar */}
      <button 
        className="mobile-nav-item mobile-menu-btn"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <FontAwesomeIcon icon="bars" className="mobile-nav-icon" />
        <span className="mobile-nav-label">Menu</span>
      </button>
    </nav>
  )
}

export default MobileNav
