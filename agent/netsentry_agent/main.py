#!/usr/bin/env python3
"""
NetSentry Local Agent - Main Entry Point
"""

import time
import logging
import sys
import os

# Ensure proper import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from netsentry_agent.config import AgentConfig
except ImportError:
    from config import AgentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main agent loop"""
    print("\n" + "=" * 60)
    print("NetSentry Local Agent Starting")
    print("=" * 60 + "\n")
    
    # Validate configuration
    try:
        AgentConfig.validate()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    print(f"📡 Backend URL: {AgentConfig.BACKEND_URL}")
    print(f"🔑 Agent API Key: {'*' * len(AgentConfig.AGENT_API_KEY)}")
    print(f"⏱️  Scan Interval: {AgentConfig.SCAN_INTERVAL}s")
    print(f"📊 Traffic Interval: {AgentConfig.TRAFFIC_INTERVAL}s")
    print(f"🌐 Network Interface: {AgentConfig.NETWORK_INTERFACE}")
    
    print("\n" + "=" * 60)
    print("Agent initialized successfully")
    print("Waiting for Phase 4 implementation...")
    print("=" * 60 + "\n")
    
    # Keep the agent running
    try:
        counter = 0
        while True:
            time.sleep(10)
            counter += 1
            print(f"⏳ Agent running... (heartbeat {counter})")
    except KeyboardInterrupt:
        print("\n⏹️  Agent stopped by user")
        return 0

if __name__ == '__main__':
    sys.exit(main())
