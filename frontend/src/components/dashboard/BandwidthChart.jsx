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

const BandwidthChart = ({ data, loading }) => {
  if (loading) {
    return (
      <div style={{ height: '140px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)' }}>Loading...</p>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ height: '140px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)' }}>No data available</p>
      </div>
    )
  }

  const chartData = {
    labels: data.map(d => {
      const date = new Date(d.timestamp)
      return date.toLocaleTimeString()
    }).reverse(),
    datasets: [
      {
        label: 'Bandwidth (Mbps)',
        data: data.map(d => d.bandwidth_mbps || 0).reverse(),
        borderColor: '#00D26A',
        backgroundColor: 'rgba(0, 210, 106, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 1,
        pointBackgroundColor: '#00D26A',
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
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
        display: false,
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 9 } },
        beginAtZero: true,
      }
    },
  }

  return (
    <div style={{ height: '140px' }}>
      <Line data={chartData} options={options} />
    </div>
  )
}

export default BandwidthChart
