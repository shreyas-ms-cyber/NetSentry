import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <div style={{ 
        minHeight: '100vh', 
        background: '#0B1120', 
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ color: '#00E5FF', fontFamily: 'Poppins, sans-serif' }}>
            NetSentry
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.6)' }}>
            Network Monitoring Dashboard
          </p>
          <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '14px', marginTop: '20px' }}>
            🚀 Phase 2 Complete - Backend and Agent configured
          </p>
          <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: '12px' }}>
            Frontend ready for Phase 9 implementation
          </p>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
