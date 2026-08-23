import React, { useState, useEffect } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { getDashboardSummary, getTraffic, getAlerts } from '../services/api'
import { getCached, setCached } from '../utils/cache'
import TrafficChart from '../components/dashboard/TrafficChart'
import ProtocolChart from '../components/dashboard/ProtocolChart'
import BandwidthChart from '../components/dashboard/BandwidthChart'
import TopTalkers from '../components/dashboard/TopTalkers'
import RecentEvents from '../components/dashboard/RecentEvents'
import './Dashboard.css'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(() => getCached('dashboard-summary'))
  const [trafficData, setTrafficData] = useState([])
  const [alerts, setAlerts] = useState([])
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAllData = async () => {
    try {
      setLoading(true)
      const [summaryRes, trafficRes, alertsRes] = await Promise.all([
        getDashboardSummary(),
        getTraffic({ limit: 50 }),
        getAlerts({ acknowledged: false })
      ])

      // SAFETY: Extract traffic array correctly
      let trafficArray = []
      if (trafficRes?.data) {
        if (Array.isArray(trafficRes.data)) {
          trafficArray = trafficRes.data
        } else if (trafficRes.data.traffic && Array.isArray(trafficRes.data.traffic)) {
          trafficArray = trafficRes.data.traffic
        }
      }

      // SAFETY: Extract alerts array correctly
      let alertsArray = []
      if (alertsRes?.data) {
        if (Array.isArray(alertsRes.data)) {
          alertsArray = alertsRes.data
        } else if (alertsRes.data.alerts && Array.isArray(alertsRes.data.alerts)) {
          alertsArray = alertsRes.data.alerts
        }
      }

      // Find the best entry (first with non-zero protocol breakdown)
      const bestTrafficEntry = trafficArray.find(entry => {
        const pb = entry.protocol_breakdown || {}
        return pb.tcp > 0 || pb.udp > 0 || pb.icmp > 0 || pb.other > 0
      }) || trafficArray[0] || null

      const mergedSummary = {
        ...summaryRes.data,
        latest_traffic: bestTrafficEntry || summaryRes.data?.latest_traffic
      }

      setSummary(mergedSummary)
      setTrafficData(trafficArray)
      setAlerts(alertsArray)
      setLastUpdated(new Date())

      setCached('dashboard-summary', mergedSummary, 30)
      setCached('traffic-data', trafficArray, 30)
      setCached('alerts-data', alertsArray, 30)

    } catch (err) {
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  // ... rest of component remains the same
}
