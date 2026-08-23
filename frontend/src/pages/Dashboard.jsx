import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getDashboardSummary, getTraffic, getAlerts } from '../services/api'
import { getCached, setCached } from '../utils/cache'
import './Dashboard.css'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(() => getCached('dashboard-summary'))
  const [trafficData, setTrafficData] = useState(() => getCached('traffic-data') || [])
  const [alerts, setAlerts] = useState(() => getCached('alerts-data') || [])
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAllData = async () => {
    try {
      setLoading(true)
      const [summaryRes, trafficRes, alertsRes] = await Promise.all([
        getDashboardSummary(),
        getTraffic({ limit: 50 }),
        getAlerts({ acknowledged: false })
      ])

      // --- Extract traffic array correctly ---
      let trafficArray = []
      if (trafficRes?.data) {
        if (Array.isArray(trafficRes.data)) {
          trafficArray = trafficRes.data
        } else if (trafficRes.data.traffic && Array.isArray(trafficRes.data.traffic)) {
          trafficArray = trafficRes.data.traffic
        }
      }

      // Find the best entry (first with non-zero protocol breakdown)
      const bestTrafficEntry = trafficArray.find(entry => {
        const pb = entry.protocol_breakdown || {}
        return pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0
      }) || trafficArray[0] || null

      // Merge summary with the best traffic entry for chart/breakdown/talkers
      const mergedSummary = {
        ...summaryRes.data,
        latest_traffic: bestTrafficEntry || summaryRes.data?.latest_traffic
      }

      setSummary(mergedSummary)
      setTrafficData(trafficArray)
      setAlerts(alertsRes.data || [])
      setLastUpdated(new Date())

      // Cache for 30 seconds
      setCached('dashboard-summary', mergedSummary, 30)
      setCached('traffic-data', trafficArray, 30)
      setCached('alerts-data', alertsRes.data || [], 30)

    } catch (err) {
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  // ... (rest of component remains identical, using summary, trafficData, alerts)
  // The protocol breakdown, top talkers, and chart will now use the best entry.
}
