import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './About.css'

const About = () => {
  return (
    <div className="about-page">
      <div className="about-header">
        <h1 className="about-title">About NetSentry</h1>
        <p className="about-subtitle">Network Monitoring & Security Intelligence Platform</p>
      </div>

      <div className="about-grid">
        <div className="about-card">
          <h2 className="about-card-title">What is NetSentry?</h2>
          <p className="about-card-text">
            NetSentry is a professional network monitoring and security-visibility platform 
            that discovers devices on an authorized local network, identifies visible/open ports, 
            collects near-real-time network traffic statistics, detects important network changes, 
            and presents the results through a premium SOC/NOC-style web dashboard.
          </p>
        </div>

        <div className="about-card">
          <h2 className="about-card-title">Architecture</h2>
          <div className="architecture-flow">
            <div className="flow-item">
              <span className="flow-icon">🖥️</span>
              <span>Authorized Local Network</span>
            </div>
            <div className="flow-arrow">↓</div>
            <div className="flow-item">
              <span className="flow-icon">🤖</span>
              <span>NetSentry Local Agent</span>
              <span className="flow-desc">ARP Discovery · Port Scanning · Packet Capture</span>
            </div>
            <div className="flow-arrow">↓</div>
            <div className="flow-item">
              <span className="flow-icon">🔒</span>
              <span>HTTPS + X-Agent-Key</span>
            </div>
            <div className="flow-arrow">↓</div>
            <div className="flow-item">
              <span className="flow-icon">⚡</span>
              <span>Flask Backend</span>
              <span className="flow-desc">Validation · Storage · API</span>
            </div>
            <div className="flow-arrow">↓</div>
            <div className="flow-item">
              <span className="flow-icon">🗄️</span>
              <span>PostgreSQL Database</span>
            </div>
            <div className="flow-arrow">↓</div>
            <div className="flow-item">
              <span className="flow-icon">🎨</span>
              <span>React Dashboard</span>
              <span className="flow-desc">SOC/NOC Visualization</span>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2 className="about-card-title">Technology Stack</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <span className="tech-icon">⚛️</span>
              <span>React 18</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">🐍</span>
              <span>Python 3.11</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">🔬</span>
              <span>Scapy</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">📊</span>
              <span>Chart.js</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">🔥</span>
              <span>Flask 3.0</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">🐘</span>
              <span>PostgreSQL</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">📦</span>
              <span>SQLAlchemy</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">🎨</span>
              <span>Bootstrap 5</span>
            </div>
          </div>
        </div>

        <div className="about-card developer">
          <h2 className="about-card-title">Built by</h2>
          <div className="developer-info">
            <div className="developer-avatar">
              <span>SM</span>
            </div>
            <div className="developer-details">
              <h3 className="developer-name">Shreyas M S</h3>
              <p className="developer-role">Cybersecurity Analyst · SOC Operations · Network Security</p>
              <div className="developer-links">
                <a href="https://github.com/shreyas-ms-cyber" target="_blank" rel="noopener noreferrer">
                  <FontAwesomeIcon icon={['fab', 'github']} />
                  GitHub
                </a>
                <a href="https://linkedin.com/in/shreyas-ms" target="_blank" rel="noopener noreferrer">
                  <FontAwesomeIcon icon={['fab', 'linkedin']} />
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default About
