"""
NetSentry Backend Application
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# Initialize db
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Get database URL
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and 'postgresql' in database_url:
        # For psycopg v3, use the correct driver prefix
        if not database_url.startswith('postgresql+psycopg'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')
        print(f"📊 Using PostgreSQL with psycopg v3 driver")
    elif not database_url:
        database_url = 'sqlite:///netsentry.db'
        print("⚠️  DATABASE_URL not set, using SQLite")
    
    print(f"📊 Using database: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if 'sqlite' in database_url:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False}
        }
    
    # CORS
    cors_origin = os.environ.get('CORS_ORIGIN', '*')
    CORS(app, 
         resources={r"/*": {"origins": cors_origin if cors_origin != '*' else '*'}},
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'X-Agent-Key']
    )
    
    # Initialize db with app
    db.init_app(app)
    
    # Import models and create tables
    with app.app_context():
        from app.models import Device, PortScan, TrafficStat, Alert
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Import and register blueprints
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
