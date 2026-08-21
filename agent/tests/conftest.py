"""
Pytest configuration for NetSentry Agent
"""

import sys
import os

# Add the parent directory to path so netsentry_agent can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import from netsentry_agent
from netsentry_agent import config
