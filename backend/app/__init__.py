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
    
    # FORCE SQLITE - No PostgreSQL
    database_url = 'sqlite:///netsentry.db'
    print(f"📊 Using database: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'check_same_thread': False}
    }
    
    # CORS - Allow all
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize db with app
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Import models
    from app.models import Device, PortScan, TrafficStat, Alert
    
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
