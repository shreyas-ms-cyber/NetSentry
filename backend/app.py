"""
NetSentry Backend - Standalone Working Version
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# Create db instance
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and 'postgresql' in database_url:
        if not database_url.startswith('postgresql+psycopg'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')
        print(f"📊 Using PostgreSQL")
    else:
        database_url = 'sqlite:///netsentry.db'
        print("⚠️  Using SQLite")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if 'sqlite' in database_url:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False}
        }
    
    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize db with app
    db.init_app(app)
    
    # Define models INSIDE the function to avoid import issues
    class Device(db.Model):
        __tablename__ = 'devices'
        id = db.Column(db.Integer, primary_key=True)
        ip_address = db.Column(db.String(45), nullable=False)
        mac_address = db.Column(db.String(17), nullable=False)
        vendor = db.Column(db.String(100))
        hostname = db.Column(db.String(255))
        status = db.Column(db.String(20), default='ONLINE')
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    # Routes
    @app.route('/')
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'NetSentry Backend'})
    
    @app.route('/api/test')
    def test():
        try:
            count = Device.query.count()
            return jsonify({'message': 'Database working!', 'device_count': count})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dashboard/summary')
    def dashboard_summary():
        try:
            total_devices = Device.query.count()
            return jsonify({
                'total_devices': total_devices,
                'online_devices': 0,
                'offline_devices': 0,
                'open_ports': 0,
                'latest_traffic': None,
                'unacknowledged_alerts': 0
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/devices')
    def get_devices():
        try:
            devices = Device.query.all()
            return jsonify({
                'devices': [{'id': d.id, 'ip': d.ip_address} for d in devices],
                'count': len(devices)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
