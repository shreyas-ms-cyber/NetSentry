"""
API Client - Handles communication with NetSentry Backend
"""

import logging
import requests
import time
from datetime import datetime

from netsentry_agent.config import AgentConfig

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with NetSentry backend"""
    
    def __init__(self):
        self.base_url = AgentConfig.BACKEND_URL
        self.api_key = AgentConfig.AGENT_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'X-Agent-Key': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _request(self, method, endpoint, data=None, retries=3, delay=1):
        """Make authenticated request to backend with retries"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        
        for attempt in range(retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 401:
                    logger.error("❌ Authentication failed - Check AGENT_API_KEY")
                    return None
                else:
                    logger.warning(f"Request failed: {response.status_code} - {response.text[:100]}")
                    if attempt < retries - 1:
                        time.sleep(delay * (attempt + 1))
                    continue
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                continue
            except Exception as e:
                logger.error(f"Request error: {e}")
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
                continue
        
        logger.error(f"❌ All retries failed for {method} {endpoint}")
        return None
    
    def ping(self):
        """Check if backend is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def ingest_devices(self, devices):
        """Send discovered devices to backend"""
        if not devices:
            return True
        
        logger.info(f"📤 Sending {len(devices)} devices to backend...")
        
        chunk_size = 50
        success_count = 0
        
        for i in range(0, len(devices), chunk_size):
            chunk = devices[i:i + chunk_size]
            data = {'devices': chunk}
            
            result = self._request('POST', 'devices/ingest', data)
            
            if result:
                success_count += len(chunk)
                logger.info(f"✅ Successfully ingested {success_count}/{len(devices)} devices")
            else:
                logger.error(f"❌ Failed to ingest device chunk {i//chunk_size + 1}")
        
        return success_count == len(devices)
    
    def ingest_port_scans(self, port_scans):
        """Send port scan results to backend"""
        if not port_scans:
            return True
        
        logger.info(f"📤 Sending {len(port_scans)} port scans to backend...")
        
        data = {'port_scans': port_scans}
        result = self._request('POST', 'ports/ingest', data)
        
        if result:
            logger.info(f"✅ Successfully ingested {len(port_scans)} port scans")
            return True
        else:
            logger.error("❌ Failed to ingest port scans")
            return False
    
    def ingest_traffic(self, traffic_data):
        """Send traffic statistics to backend"""
        if not traffic_data:
            return True
        
        logger.info(f"📤 Sending traffic stats to backend...")
        
        result = self._request('POST', 'traffic/ingest', traffic_data)
        
        if result:
            logger.info("✅ Successfully ingested traffic stats")
            return True
        else:
            logger.error("❌ Failed to ingest traffic stats")
            return False

def test_api_connection():
    """Test API connection"""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 60)
    print("Testing API Connection")
    print("=" * 60 + "\n")
    
    client = APIClient()
    
    print(f"Testing connection to: {client.base_url}")
    if client.ping():
        print("✅ Backend is reachable!")
    else:
        print("❌ Cannot reach backend!")
        return False
    
    # Test device ingestion
    test_device = [{
        'ip_address': '192.168.1.99',
        'mac_address': 'AA:BB:CC:DD:EE:99',
        'vendor': 'Test Vendor',
        'hostname': 'test-device',
        'status': 'ONLINE'
    }]
    
    print("\nTesting device ingestion...")
    result = client.ingest_devices(test_device)
    if result:
        print("✅ Device ingestion successful!")
    else:
        print("❌ Device ingestion failed!")
    
    return True
