#!/usr/bin/env python3
"""
NetSentry Backend Server
Run with: python run.py
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    print(f"🚀 NetSentry Backend starting on port {port}")
    print(f"🔧 Debug mode: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
