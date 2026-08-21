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

# Initialize db
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and 'postgresql' in database_url:
        # For psycopg v3, use the correct driver prefix
        if not database_url.startswith('postgresql+psycopg'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')
        print(f"📊 Using PostgreSQL with psycopg v3 driver")
    else:
        database_url = 'sqlite:///netsentry.db'
        print("⚠️  DATABASE_URL not set, using SQLite")
    
    print(f"📊 Using database: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if 'sqlite' in database_url:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False}
        }
    
    # CORS - Allow all origins
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize db with app
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        from app.models import Device, PortScan, TrafficStat, Alert
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
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
