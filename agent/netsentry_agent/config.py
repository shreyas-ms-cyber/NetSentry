"""
Agent configuration management
"""

import os
from dotenv import load_dotenv

# Load .env from parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

class AgentConfig:
    """Agent configuration"""
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5000')
    AGENT_API_KEY = os.environ.get('AGENT_API_KEY')
    SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', 60))
    TRAFFIC_INTERVAL = int(os.environ.get('TRAFFIC_INTERVAL', 10))
    NETWORK_INTERFACE = os.environ.get('NETWORK_INTERFACE', 'eth0')
    DISCOVERY_TIMEOUT = int(os.environ.get('DISCOVERY_TIMEOUT', 2))
    PORT_SCAN_TIMEOUT = int(os.environ.get('PORT_SCAN_TIMEOUT', 1))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.AGENT_API_KEY:
            raise ValueError("AGENT_API_KEY is required")
        if not cls.BACKEND_URL:
            raise ValueError("BACKEND_URL is required")
        if cls.AGENT_API_KEY == 'change-this-to-a-strong-secret-key-in-production':
            raise ValueError("AGENT_API_KEY must be changed from default value")
        return True
