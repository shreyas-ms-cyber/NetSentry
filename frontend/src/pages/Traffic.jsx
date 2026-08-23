import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getTraffic } from '../services/api'
import './Traffic.css'

const Traffic = () => {
  const [loading, setLoading] = useState(true)
  const [trafficData, setTrafficData] = useState([])
  const [error, setError] = useState(null)

  const fetchTraffic = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getTraffic({ limit: 100 })

      // Extract the traffic array
      let data = []
      if (response?.data) {
        if (Array.isArray(response.data)) {
          data = response.data
        } else if (response.data.traffic && Array.isArray(response.data.traffic)) {
          data = response.data.traffic
        }
      }

      console.log('Traffic Data:', data)
      setTrafficData(data)
    } catch (err) {
      console.error('Error fetching traffic:', err)
      setError('Failed to load traffic data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTraffic()
  }, [])

  // Find best entry (non-zero protocol breakdown)
  const findDisplayEntry = () => {
    if (!trafficData || trafficData.length === 0) return null
    for (const entry of trafficData) {
      const pb = entry.protocol_breakdown || {}
      if (pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0) {
        return entry
      }
    }
    return trafficData[0] || null
  }

  const displayEntry = findDisplayEntry()
  const protocolBreakdown = displayEntry?.protocol_breakdown || { tcp: 0, udp: 0, icmp: 0, other: 0 }
  const topTalkers = displayEntry?.top_talkers || []

  // ... the rest of the component uses displayEntry for protocol breakdown and talkers
  // and trafficData for the chart

  return (
    <div className="traffic-page">
      {/* header, stats, chart, protocol, talkers – all use the corrected data */}
    </div>
  )
}
