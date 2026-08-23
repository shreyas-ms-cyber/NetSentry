import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const TrafficChart = ({ data, loading }) => {
  // SAFETY: Ensure data is always an array
  const safeData = Array.isArray(data) ? data : []

  if (loading) {
    return (
      <div className="chart-container" style={{ height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)' }}>Loading...</p>
      </div>
    )
  }

  if (safeData.length === 0) {
    return (
      <div className="chart-container" style={{ height: '280px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.3)', marginBottom: '8px' }}>No network telemetry available</p>
        <p style={{ color: 'rgba(255,255,255,0.15)', fontSize: '13px' }}>Start the NetSentry Local Agent to begin monitoring</p>
      </div>
    )
  }

  const chartData = {
    labels: safeData.map(d => {
      const date = new Date(d.timestamp)
      return date.toLocaleTimeString()
    }).reverse(),
    datasets: [
      {
        label: 'Packets/sec',
        data: safeData.map(d => d.packets_per_sec || 0).reverse(),
        borderColor: '#00E5FF',
        backgroundColor: 'rgba(0, 229, 255, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointBackgroundColor: '#00E5FF',
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: 'rgba(255,255,255,0.5)',
          font: { size: 11 }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(13, 21, 38, 0.9)',
        titleColor: '#fff',
        bodyColor: 'rgba(255,255,255,0.7)',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 10 } }
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 10 } },
        beginAtZero: true,
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  }

  return (
    <div className="chart-container" style={{ height: '280px' }}>
      <Line data={chartData} options={options} />
    </div>
  )
}

export default TrafficChart
