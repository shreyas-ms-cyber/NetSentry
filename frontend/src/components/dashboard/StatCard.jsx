import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './StatCard.css'

const StatCard = ({ title, value, icon, color = '#00E5FF', subtitle }) => {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        {icon && (
          <span className="stat-card-icon-wrapper">
            <FontAwesomeIcon icon={icon} className="stat-card-icon" style={{ color }} />
          </span>
        )}
        <span className="stat-card-label">{title}</span>
      </div>
      <div className="stat-card-value" style={{ color }}>{value}</div>
      {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
    </div>
  )
}

export default StatCard
