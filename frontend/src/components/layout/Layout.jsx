import React, { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import MobileNav from './MobileNav'
import './Layout.css'

const Layout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      if (!mobile) {
        setMobileMenuOpen(false)
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const toggleSidebar = () => {
    if (isMobile) {
      setMobileMenuOpen(!mobileMenuOpen)
    } else {
      setSidebarCollapsed(!sidebarCollapsed)
    }
  }

  const closeMobileMenu = () => {
    setMobileMenuOpen(false)
  }

  return (
    <div className="app-container">
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      )}
      
      {/* Mobile Sidebar Overlay */}
      {isMobile && mobileMenuOpen && (
        <div className="mobile-overlay" onClick={closeMobileMenu}>
          <div className="mobile-sidebar-wrapper" onClick={(e) => e.stopPropagation()}>
            <Sidebar collapsed={false} onToggle={closeMobileMenu} />
          </div>
        </div>
      )}
      
      <div className={`main-content ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Topbar onMenuClick={toggleSidebar} isMobile={isMobile} />
        <div className="page-content">
          <Outlet />
        </div>
        {isMobile && <MobileNav onMenuClick={toggleSidebar} />}
      </div>
    </div>
  )
}

export default Layout
