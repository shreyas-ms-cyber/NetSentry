"""
Flask extensions initialization
"""

from flask_sqlalchemy import SQLAlchemy

# This is the SINGLE db instance used everywhere
db = SQLAlchemy()
