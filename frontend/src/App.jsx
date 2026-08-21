import React, { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faGaugeHigh, faNetworkWired, faPlug, faChartLine, 
  faTriangleExclamation, faCircleInfo, faServer,
  faMagnifyingGlass, faBell, faCircle, faArrowRight,
  faChevronRight, faChevronLeft, faBars, faTimes,
  faCheck, faExclamation, faXmark, faClock,
  faDesktop, faLaptop, faMobile, faTablet,
  faSync, faPlusCircle, faPowerOff, faCheckCircle,
  faEllipsis, faArrowLeft, faEye, faRotate,
  faShield, faDatabase, faSatelliteDish,
  faSearch, faSpinner,
  faInfoCircle, faExclamationCircle, faExclamationTriangle,
  faGauge, faArrowsUpDown, faCloudUpload, faArrowUpDown
} from '@fortawesome/free-solid-svg-icons'
import { faGithub, faLinkedin } from '@fortawesome/free-brands-svg-icons'

library.add(
  faGaugeHigh, faNetworkWired, faPlug, faChartLine,
  faTriangleExclamation, faCircleInfo, faServer,
  faMagnifyingGlass, faBell, faCircle, faArrowRight,
  faChevronRight, faChevronLeft, faBars, faTimes,
  faCheck, faExclamation, faXmark, faClock,
  faDesktop, faLaptop, faMobile, faTablet,
  faSync, faPlusCircle, faPowerOff, faCheckCircle,
  faEllipsis, faArrowLeft, faEye, faRotate,
  faShield, faDatabase, faSatelliteDish,
  faSearch, faSpinner,
  faInfoCircle, faExclamationCircle, faExclamationTriangle,
  faGauge, faArrowsUpDown, faCloudUpload, faArrowUpDown,
  faGithub, faLinkedin
)

import Layout from './components/layout/Layout'

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Devices = lazy(() => import('./pages/Devices'))
const DeviceDetails = lazy(() => import('./pages/DeviceDetails'))
const Ports = lazy(() => import('./pages/Ports'))
const Traffic = lazy(() => import('./pages/Traffic'))
const Alerts = lazy(() => import('./pages/Alerts'))
const About = lazy(() => import('./pages/About'))
const SystemStatus = lazy(() => import('./pages/SystemStatus'))

// Loading fallback
const PageLoader = () => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    color: 'rgba(255,255,255,0.2)',
    fontSize: '14px'
  }}>
    Loading...
  </div>
)

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="devices" element={<Devices />} />
            <Route path="devices/:id" element={<DeviceDetails />} />
            <Route path="ports" element={<Ports />} />
            <Route path="traffic" element={<Traffic />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="about" element={<About />} />
            <Route path="system-status" element={<SystemStatus />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
