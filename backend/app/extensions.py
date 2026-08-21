"""
Flask extensions - SINGLE SOURCE OF TRUTH for db instance
"""

from flask_sqlalchemy import SQLAlchemy

# This is the ONE and ONLY db instance
db = SQLAlchemy()
