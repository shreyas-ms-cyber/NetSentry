"""
Flask extensions - Single source of truth for db instance
"""

from flask_sqlalchemy import SQLAlchemy

# This is the ONE db instance used everywhere
db = SQLAlchemy()
