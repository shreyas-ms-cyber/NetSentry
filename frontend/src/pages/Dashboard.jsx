import React, { useState, useEffect, useRef } from 'react'
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
  const [trafficData, setTrafficData] = useState(() => getCached('traffic-data') || [])
  const [alerts, setAlerts] = useState(() => getCached('alerts-data') || [])
  const [lastUpdated, setLastUpdated] = useState(null)
  const [error, setError] = useState(null)
  const fetchCount = useRef(0)

  const fetchAllData = async (retryCount = 0) => {
    try {
      setLoading(true)
      setError(null)
      fetchCount.current += 1
      
      console.log(`Fetch attempt ${fetchCount.current}...`)
      
      const [summaryRes, trafficRes, alertsRes] = await Promise.all([
        getDashboardSummary(),
        getTraffic({ limit: 50 }),
        getAlerts({ acknowledged: false })
      ])

      let trafficArray = []
      if (trafficRes?.data) {
        if (Array.isArray(trafficRes.data)) {
          trafficArray = trafficRes.data
        } else if (trafficRes.data.traffic && Array.isArray(trafficRes.data.traffic)) {
          trafficArray = trafficRes.data.traffic
        }
      }

      let alertsArray = []
      if (alertsRes?.data) {
        if (Array.isArray(alertsRes.data)) {
          alertsArray = alertsRes.data
        } else if (alertsRes.data.alerts && Array.isArray(alertsRes.data.alerts)) {
          alertsArray = alertsRes.data.alerts
        }
      }

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
      
      // Retry up to 3 times on timeout
      if (retryCount < 3 && (err.code === 'ECONNABORTED' || err.message?.includes('timeout'))) {
        console.log(`Retrying... (attempt ${retryCount + 2})`)
        await new Promise(resolve => setTimeout(resolve, 2000 * (retryCount + 1)))
        return fetchAllData(retryCount + 1)
      }
      
      setError('Failed to load data. Please refresh the page.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  // ... rest of the component remains the same
}
