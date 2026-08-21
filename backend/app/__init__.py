"""
NetSentry Backend Application
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize db as None - will be set in create_app
db = SQLAlchemy()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration - Use PostgreSQL or SQLite fallback
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and 'postgresql' in database_url:
        # For PostgreSQL with psycopg 3.x, use the correct driver
        if not database_url.startswith('postgresql+psycopg'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')
        print(f"📊 Using PostgreSQL with psycopg driver")
    elif not database_url:
        database_url = 'sqlite:///netsentry.db'
        print("⚠️  DATABASE_URL not set, using SQLite")
    
    print(f"📊 Using database: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # SQLite specific settings
    if 'sqlite' in database_url:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False}
        }
    
    # CORS - Allow all origins for development
    cors_origin = os.environ.get('CORS_ORIGIN', '*')
    CORS(app, 
         resources={r"/*": {"origins": cors_origin if cors_origin != '*' else '*'}},
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'X-Agent-Key', 'Authorization']
    )
    
    # Initialize db with app - THIS IS THE KEY FIX
    db.init_app(app)
    
    # Import models AFTER db initialization
    from app.models import Device, PortScan, TrafficStat, Alert
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Import and register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'NetSentry Backend', 'version': '1.0.0'})
    
    @app.route('/')
    def index():
        return jsonify({
            'service': 'NetSentry Backend',
            'version': '1.0.0',
            'status': 'running'
        })
    
    return app
