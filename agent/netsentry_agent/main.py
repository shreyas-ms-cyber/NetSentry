#!/usr/bin/env python3
"""
NetSentry Local Agent - Main Entry Point
"""

import time
import logging
import sys
import os
import signal
from datetime import datetime, timezone

# Ensure proper import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from netsentry_agent.config import AgentConfig
    from netsentry_agent.discovery import DeviceDiscovery
    from netsentry_agent.scanner import PortScanner
    from netsentry_agent.traffic import TrafficMonitor
    from netsentry_agent.api_client import APIClient
    from netsentry_agent.network_scope import NetworkScopeValidator
except ImportError:
    from config import AgentConfig
    from discovery import DeviceDiscovery
    from scanner import PortScanner
    from traffic import TrafficMonitor
    from api_client import APIClient
    from network_scope import NetworkScopeValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetSentryAgent:
    """Main agent class managing discovery, scanning, and traffic monitoring"""
    
    def __init__(self):
        self.running = True
        self.discovery = DeviceDiscovery()
        self.scanner = PortScanner(timeout=1.0)
        self.traffic_monitor = TrafficMonitor()
        self.api_client = APIClient()
        self.last_scan_time = None
        self.last_traffic_push = None
        self.discovered_devices = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n🛑 Received shutdown signal")
        self.running = False
        self.traffic_monitor.stop_sniffing()
    
    def run_scan_cycle(self):
        """Run a complete scan cycle: discovery + port scanning"""
        logger.info("=" * 60)
        logger.info("Starting Discovery & Scan Cycle")
        logger.info("=" * 60)
        
        # Check backend connectivity
        if not self.api_client.ping():
            logger.warning("⚠️ Backend is not reachable. Will retry next cycle.")
            return
        
        # 1. Discover network devices
        network = self.discovery.discover_network()
        if not network:
            logger.error("❌ Could not discover network configuration")
            return
        
        devices = self.discovery.scan_network()
        
        if not devices:
            logger.info("ℹ️ No devices found on network")
            return
        
        self.discovered_devices = devices
        logger.info(f"📱 Found {len(devices)} devices")
        
        # 2. Scan ports on each device
        all_port_scans = []
        
        for device in devices:
            ip = device.get('ip_address')
            logger.info(f"\n🔍 Scanning ports on {ip}...")
            
            scanned_device = self.scanner.scan_device(device)
            
            if scanned_device.get('port_scans'):
                all_port_scans.extend(scanned_device['port_scans'])
                open_count = len([p for p in scanned_device['port_scans'] if p['status'] == 'OPEN'])
                logger.info(f"  Found {open_count} open ports on {ip}")
        
        # 3. Ingest devices to backend
        self.api_client.ingest_devices(devices)
        
        # 4. Ingest port scans to backend
        if all_port_scans:
            self.api_client.ingest_port_scans(all_port_scans)
        
        self.last_scan_time = datetime.now(timezone.utc)
        logger.info("=" * 60)
        logger.info("Discovery & Scan Cycle Complete")
        logger.info("=" * 60)
    
    def run_traffic_cycle(self):
        """Run traffic monitoring cycle"""
        try:
            # Get traffic stats
            traffic_data = self.traffic_monitor.get_traffic_stats()
            
            # Calculate traffic rates
            self.traffic_monitor.calculate_traffic()
            
            # Ingest traffic stats to backend
            self.api_client.ingest_traffic(traffic_data)
            self.last_traffic_push = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error in traffic cycle: {e}")
    
    def run(self):
        """Main agent loop"""
        print("\n" + "=" * 60)
        print("NetSentry Local Agent")
        print("Version: 1.0.0")
        print("=" * 60 + "\n")
        
        # Validate configuration
        try:
            AgentConfig.validate()
            print("✅ Configuration validated successfully")
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            return 1
        
        print(f"📡 Backend URL: {AgentConfig.BACKEND_URL}")
        print(f"🔑 Agent API Key: {'*' * min(len(AgentConfig.AGENT_API_KEY), 8)}")
        print(f"⏱️  Scan Interval: {AgentConfig.SCAN_INTERVAL}s")
        print(f"📊 Traffic Interval: {AgentConfig.TRAFFIC_INTERVAL}s")
        print(f"🔌 Port Scan Timeout: {AgentConfig.PORT_SCAN_TIMEOUT}s")
        print(f"🌐 Network Interface: {AgentConfig.NETWORK_INTERFACE}")
        
        print("\n" + "=" * 60)
        print("Agent Starting")
        print("=" * 60 + "\n")
        
        # Start traffic monitoring
        self.traffic_monitor.start_sniffing()
        
        # Run initial scan
        self.run_scan_cycle()
        
        # Main loop
        cycle_count = 0
        traffic_count = 0
        last_traffic_time = time.time()
        
        while self.running:
            try:
                # Run scan cycle at configured interval
                time.sleep(AgentConfig.SCAN_INTERVAL)
                cycle_count += 1
                print(f"\n🔄 Scan Cycle {cycle_count}")
                self.run_scan_cycle()
                
                # Run traffic monitoring at configured interval
                current_time = time.time()
                if current_time - last_traffic_time >= AgentConfig.TRAFFIC_INTERVAL:
                    traffic_count += 1
                    print(f"\n📊 Traffic Update {traffic_count}")
                    self.run_traffic_cycle()
                    last_traffic_time = current_time
                
            except KeyboardInterrupt:
                logger.info("\n⏹️  Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(10)
        
        # Cleanup
        self.traffic_monitor.stop_sniffing()
        
        print("\n" + "=" * 60)
        print("Agent Shutdown Complete")
        print("=" * 60)
        return 0

def main():
    """Entry point"""
    agent = NetSentryAgent()
    sys.exit(agent.run())

if __name__ == '__main__':
    main()
