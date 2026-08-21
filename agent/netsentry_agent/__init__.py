"""
NetSentry Local Agent
Network discovery, port scanning, and traffic telemetry
"""

from netsentry_agent.config import AgentConfig
from netsentry_agent.main import main

__version__ = '1.0.0'
__all__ = ['AgentConfig', 'main']
