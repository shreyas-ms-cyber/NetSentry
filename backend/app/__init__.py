"""
NetSentry Backend Application
"""

import os
import traceback
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# IMPORT db FROM extensions - NOT create a new one
from app.extensions import db

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and 'postgresql' in database_url:
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
    
    # Initialize db with app - THIS IS THE KEY FIX
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        try:
            from app.models import Device, PortScan, TrafficStat, Alert
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            print(traceback.format_exc())
    
    # Register blueprints
    try:
        from app.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print("✅ Routes registered successfully")
    except Exception as e:
        print(f"❌ Error registering routes: {e}")
        print(traceback.format_exc())
    
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
    
    # Test endpoint to debug database
    @app.route('/test')
    def test():
        try:
            from app.models import Device
            count = Device.query.count()
            return jsonify({'message': 'Database working!', 'device_count': count})
        except Exception as e:
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    
    return app
