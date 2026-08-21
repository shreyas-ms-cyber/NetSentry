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
        {/* What is NetSentry */}
        <div className="about-card">
          <h2 className="about-card-title">What is NetSentry?</h2>
          <p className="about-card-text">
            NetSentry is a professional network monitoring and security-visibility platform 
            that discovers devices on an authorized local network, identifies visible/open ports, 
            collects near-real-time network traffic statistics, detects important network changes, 
            and presents the results through a premium SOC/NOC-style web dashboard.
          </p>
        </div>

        {/* Key Features */}
        <div className="about-card">
          <h2 className="about-card-title">Key Features</h2>
          <div className="features-grid">
            <div className="feature-item">
              <span className="feature-icon">🔍</span>
              <div>
                <h4>Device Discovery</h4>
                <p>Automatic ARP-based device detection</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔌</span>
              <div>
                <h4>Port Scanning</h4>
                <p>Identify open ports and services</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📊</span>
              <div>
                <h4>Traffic Monitoring</h4>
                <p>Real-time network traffic analysis</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">⚡</span>
              <div>
                <h4>Alerting</h4>
                <p>Automatic security change detection</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🖥️</span>
              <div>
                <h4>SOC Dashboard</h4>
                <p>Premium command center interface</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔒</span>
              <div>
                <h4>Security Focused</h4>
                <p>Private network only, no public scanning</p>
              </div>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="about-card">
          <h2 className="about-card-title">How It Works</h2>
          <div className="how-it-works">
            <div className="step">
              <span className="step-number">1</span>
              <div className="step-content">
                <h4>Local Agent Discovery</h4>
                <p>The Local Agent scans your authorized network using ARP to discover active devices</p>
              </div>
            </div>
            <div className="step">
              <span className="step-number">2</span>
              <div className="step-content">
                <h4>Port & Traffic Analysis</h4>
                <p>Identifies open ports and monitors network traffic in real-time</p>
              </div>
            </div>
            <div className="step">
              <span className="step-number">3</span>
              <div className="step-content">
                <h4>Cloud Dashboard</h4>
                <p>Data is securely sent to the cloud dashboard for visualization and monitoring</p>
              </div>
            </div>
          </div>
        </div>

        {/* Built by */}
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
