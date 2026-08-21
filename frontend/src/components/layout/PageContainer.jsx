import React from 'react'
import './PageContainer.css'

const PageContainer = ({ title, subtitle, children, actions }) => {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header-left">
          <h2 className="page-heading">{title}</h2>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
        {actions && <div className="page-header-right">{actions}</div>}
      </div>
      <div className="page-body">
        {children}
      </div>
    </div>
  )
}

export default PageContainer
