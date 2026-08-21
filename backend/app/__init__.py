"""
NetSentry Backend Application
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import db from extensions (the single instance)
from app.extensions import db

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration - Use SQLite by default
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///netsentry.db')
    print(f"📊 Using database: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # SQLite specific settings
    if 'sqlite' in database_url:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False}
        }
    
    # CORS
    cors_origin = os.environ.get('CORS_ORIGIN', 'http://localhost:5173')
    CORS(app, origins=[cors_origin])
    
    # Initialize db with app
    db.init_app(app)
    
    # Import models (after db is initialized)
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
            'status': 'running',
            'endpoints': ['/health', '/api/health', '/api/devices', '/api/ports', '/api/traffic', '/api/alerts']
        })
    
    return app
