import { useState, useEffect, useRef, useCallback } from 'react'

export const usePolling = (fetchFn, interval = 30000, dependencies = []) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const mounted = useRef(true)
  const intervalRef = useRef(null)
  const isFetching = useRef(false)
  const fetchTimeoutRef = useRef(null)

  const fetchData = useCallback(async () => {
    if (isFetching.current) return
    if (!mounted.current) return
    
    try {
      isFetching.current = true
      setLoading(true)
      const response = await fetchFn()
      if (mounted.current) {
        setData(response.data)
        setError(null)
        setLastUpdated(new Date())
      }
    } catch (err) {
      if (mounted.current) {
        setError(err.message || 'Failed to fetch data')
      }
    } finally {
      if (mounted.current) {
        setLoading(false)
      }
      isFetching.current = false
    }
  }, [fetchFn])

  useEffect(() => {
    mounted.current = true
    
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    
    // Initial fetch with small delay to avoid blocking
    fetchTimeoutRef.current = setTimeout(() => {
      fetchData()
    }, 100)

    // Setup polling interval
    intervalRef.current = setInterval(() => {
      fetchData()
    }, interval)

    return () => {
      mounted.current = false
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current)
        fetchTimeoutRef.current = null
      }
    }
  }, [fetchData, interval, ...dependencies])

  return { data, loading, error, lastUpdated, refetch: fetchData }
}

export default usePolling
