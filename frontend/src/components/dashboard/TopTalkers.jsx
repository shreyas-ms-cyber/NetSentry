import React from 'react'
import './TopTalkers.css'

const TopTalkers = ({ data, loading }) => {
  // If no data from API, use sample data
  const safeData = Array.isArray(data) && data.length > 0 ? data : [
    { ip: '10.161.161.1', bytes: 5242880, packets: 5000, bytes_mb: 5.0 },
    { ip: '10.161.161.59', bytes: 3145728, packets: 3000, bytes_mb: 3.0 },
    { ip: '10.161.161.100', bytes: 1048576, packets: 1000, bytes_mb: 1.0 },
    { ip: '10.161.161.200', bytes: 524288, packets: 500, bytes_mb: 0.5 }
  ]

  if (loading) {
    return (
      <div style={{ padding: '8px 0' }}>
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="talker-item">
            <div className="talker-info">
              <span className="talker-ip" style={{ color: 'rgba(255,255,255,0.2)' }}>Loading...</span>
            </div>
          </div>
        ))}
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
