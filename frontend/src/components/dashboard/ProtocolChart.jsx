import React from 'react'
import { Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const ProtocolChart = ({ data, loading }) => {
  if (loading) {
    return (
      <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)' }}>Loading...</p>
      </div>
    )
  }

  if (!data || !data.protocol_breakdown) {
    return (
      <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'rgba(255,255,255,0.2)' }}>No data available</p>
      </div>
    )
  }

  const breakdown = data.protocol_breakdown || { tcp: 0, udp: 0, icmp: 0, other: 0 }
  
  const chartData = {
    labels: ['TCP', 'UDP', 'ICMP', 'Other'],
    datasets: [
      {
        data: [breakdown.tcp || 0, breakdown.udp || 0, breakdown.icmp || 0, breakdown.other || 0],
        backgroundColor: [
          'rgba(0, 229, 255, 0.8)',
          'rgba(255, 200, 87, 0.8)',
          'rgba(0, 210, 106, 0.8)',
          'rgba(255, 255, 255, 0.2)',
        ],
        borderColor: [
          '#00E5FF',
          '#FFC857',
          '#00D26A',
          'rgba(255,255,255,0.1)',
        ],
        borderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgba(255,255,255,0.5)',
          font: { size: 11 },
          padding: 16,
          usePointStyle: true,
        }
      },
      tooltip: {
        backgroundColor: 'rgba(13, 21, 38, 0.9)',
        titleColor: '#fff',
        bodyColor: 'rgba(255,255,255,0.7)',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0
            return `${context.label}: ${percentage}%`
          }
        }
      }
    },
    cutout: '60%',
  }

  // Calculate total packets for center text
  const totalPackets = Object.values(breakdown).reduce((a, b) => a + b, 0)

  return (
    <div style={{ position: 'relative', height: '220px' }}>
      <Doughnut data={chartData} options={options} />
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '20px', fontWeight: 600, color: '#fff' }}>
          {totalPackets > 0 ? totalPackets : '—'}
        </div>
        <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Total Packets
        </div>
      </div>
    </div>
  )
}

export default ProtocolChart
