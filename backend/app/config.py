"""
Application configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AGENT_API_KEY = os.environ.get('AGENT_API_KEY')
    CORS_ORIGIN = os.environ.get('CORS_ORIGIN', 'http://localhost:5173')
    
    @staticmethod
    def is_development():
        return os.environ.get('FLASK_ENV') == 'development'
