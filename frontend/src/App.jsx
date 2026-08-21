import React from 'react'
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
  faInfoCircle, faExclamationCircle, faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons'
import { 
  faGithub, 
  faLinkedin 
} from '@fortawesome/free-brands-svg-icons'

// Add icons to library
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
  faGithub, faLinkedin
)

import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Devices from './pages/Devices'
import DeviceDetails from './pages/DeviceDetails'
import Ports from './pages/Ports'
import Traffic from './pages/Traffic'
import Alerts from './pages/Alerts'
import About from './pages/About'
import SystemStatus from './pages/SystemStatus'

function App() {
  return (
    <BrowserRouter>
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
    </BrowserRouter>
  )
}

export default App
