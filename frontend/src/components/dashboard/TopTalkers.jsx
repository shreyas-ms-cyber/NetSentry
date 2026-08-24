import React from 'react'
import './TopTalkers.css'

const TopTalkers = ({ data, loading }) => {
  // SAFETY: Ensure data is always an array
  const safeData = Array.isArray(data) ? data : []

  if (loading) {
    return (
      <div style={{ padding: '8px 0' }}>
        {[1, 2, 3].map(i => (
          <div key={i} className="talker-item">
            <div className="talker-info">
              <span className="talker-ip" style={{ color: 'rgba(255,255,255,0.2)' }}>Loading...</span>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (safeData.length === 0) {
    return (
      <div style={{ padding: '20px 0', textAlign: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)', fontSize: '13px' }}>No traffic data available</p>
        <p style={{ color: 'rgba(255,255,255,0.08)', fontSize: '11px' }}>Start the Local Agent to collect traffic</p>
      </div>
    )
  }

  const maxBytes = safeData.length > 0 ? Math.max(...safeData.map(d => d.bytes_mb || 0)) : 1

  return (
    <div className="top-talkers">
      {safeData.slice(0, 5).map((talker, index) => {
        const bytes = talker.bytes_mb || 0
        const percentage = maxBytes > 0 ? (bytes / maxBytes) * 100 : 0
        return (
          <div key={talker.ip || index} className="talker-item">
            <div className="talker-info">
              <span className="talker-ip">{talker.ip || 'Unknown'}</span>
              <span className="talker-traffic">{bytes.toFixed(1) || '0'} MB</span>
            </div>
            <div className="talker-bar-track">
              <div 
                className="talker-bar-fill" 
                style={{ width: `${Math.min(percentage, 100)}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default TopTalkers
