import React from 'react'
import './StatCard.css'

const StatCard = ({ title, value, icon, color = '#00E5FF', subtitle }) => {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>
        {icon && <span className="stat-card-icon" style={{ color }}>{icon}</span>}
      </div>
      <div className="stat-card-value" style={{ color }}>{value}</div>
      {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
    </div>
  )
}

export default StatCard
