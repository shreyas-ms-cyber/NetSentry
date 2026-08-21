import React from 'react'
import './TopTalkers.css'

const TopTalkers = ({ data, loading }) => {
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

  if (!data || data.length === 0) {
    return (
      <div style={{ padding: '20px 0', textAlign: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)', fontSize: '13px' }}>No traffic data available</p>
      </div>
    )
  }

  const maxBytes = data.length > 0 ? Math.max(...data.map(d => d.bytes_mb || 0)) : 1

  return (
    <div className="top-talkers">
      {data.slice(0, 5).map((talker, index) => {
        const percentage = maxBytes > 0 ? ((talker.bytes_mb || 0) / maxBytes) * 100 : 0
        return (
          <div key={talker.ip || index} className="talker-item">
            <div className="talker-info">
              <span className="talker-ip">{talker.ip || 'Unknown'}</span>
              <span className="talker-traffic">{talker.bytes_mb?.toFixed(1) || '0'} MB</span>
            </div>
            <div className="talker-bar-track">
              <div 
                className="talker-bar-fill" 
                style={{ width: `${Math.min(percentage, 100)}%` }}
              ></div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default TopTalkers
