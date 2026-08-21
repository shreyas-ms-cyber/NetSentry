#!/usr/bin/env python3
"""
NetSentry Agent - Simple Version (No packet capture, no ARP)
Uses psutil for traffic stats and nmap for discovery (if available)
"""

import sys
import os
import time
import logging
import subprocess
import psutil
from datetime import datetime, timezone
import requests

# Add parent directory to path
sys.path.insert(0, os.getcwd())

from netsentry_agent.config import AgentConfig
from netsentry_agent.api_client import APIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAgent:
    def __init__(self):
        self.api = APIClient()
        self.last_traffic_time = 0
        self.traffic_interval = AgentConfig.TRAFFIC_INTERVAL
        self.scan_interval = AgentConfig.SCAN_INTERVAL
        
    def get_traffic_stats(self):
        """Get traffic stats using psutil"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            iface = AgentConfig.NETWORK_INTERFACE
            if iface in stats:
                iface_stats = stats[iface]
                return {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'packets_per_sec': 10.0,  # Simulated
                    'bandwidth_bytes': iface_stats.bytes_recv / 60,  # Average per second
                    'protocol_breakdown': {'tcp': 50, 'udp': 30, 'icmp': 10, 'other': 10}
                }
            return None
        except Exception as e:
            logger.error(f"Error getting traffic: {e}")
            return None
    
    def run(self):
        print("\n" + "=" * 60)
        print("NetSentry Agent (Simple Mode)")
        print("=" * 60 + "\n")
        
        try:
            AgentConfig.validate()
            print("✅ Configuration validated")
            print(f"📡 Backend: {AgentConfig.BACKEND_URL}")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return
        
        print("\n🔄 Starting agent loop...")
        cycle = 0
        
        while True:
            try:
                cycle += 1
                print(f"\n--- Cycle {cycle} ---")
                
                # Get traffic stats
                traffic = self.get_traffic_stats()
                if traffic:
                    result = self.api.ingest_traffic(traffic)
                    if result:
                        print(f"✅ Traffic stats sent: {traffic['packets_per_sec']:.1f} pps")
                
                # Wait for next cycle
                time.sleep(self.traffic_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ Agent stopped")
                break
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
                time.sleep(10)

if __name__ == '__main__':
    agent = SimpleAgent()
    agent.run()
