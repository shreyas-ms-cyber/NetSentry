"""
WSGI entry point for production - Root level
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

# Now import from app
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
