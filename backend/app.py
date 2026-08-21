"""
NetSentry Backend - Complete Working Version
"""

import os
import traceback
from datetime import datetime, timezone
from flask import Flask, jsonify, request
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
    
    # ============ MODELS ============
    class Device(db.Model):
        __tablename__ = 'devices'
        id = db.Column(db.Integer, primary_key=True)
        ip_address = db.Column(db.String(45), nullable=False, index=True)
        mac_address = db.Column(db.String(17), nullable=False, index=True)
        vendor = db.Column(db.String(100))
        hostname = db.Column(db.String(255))
        first_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        status = db.Column(db.String(20), default='ONLINE')
        
        def to_dict(self):
            return {
                'id': self.id,
                'ip_address': self.ip_address,
                'mac_address': self.mac_address,
                'vendor': self.vendor,
                'hostname': self.hostname,
                'first_seen': self.first_seen.isoformat() if self.first_seen else None,
                'last_seen': self.last_seen.isoformat() if self.last_seen else None,
                'status': self.status,
                'open_ports_count': 0
            }
    
    class PortScan(db.Model):
        __tablename__ = 'port_scans'
        id = db.Column(db.Integer, primary_key=True)
        device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
        port = db.Column(db.Integer, nullable=False)
        protocol = db.Column(db.String(10), nullable=False)
        status = db.Column(db.String(20), nullable=False)
        scanned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        
        def to_dict(self):
            return {
                'id': self.id,
                'device_id': self.device_id,
                'port': self.port,
                'protocol': self.protocol,
                'status': self.status,
                'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None
            }
    
    class TrafficStat(db.Model):
        __tablename__ = 'traffic_stats'
        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        packets_per_sec = db.Column(db.Float)
        bandwidth_bytes = db.Column(db.Float)
        protocol_breakdown = db.Column(db.JSON)
        
        def to_dict(self):
            return {
                'id': self.id,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None,
                'packets_per_sec': self.packets_per_sec,
                'bandwidth_bytes': self.bandwidth_bytes,
                'bandwidth_mbps': round((self.bandwidth_bytes or 0) * 8 / 1000000, 2),
                'protocol_breakdown': self.protocol_breakdown or {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0}
            }
    
    class Alert(db.Model):
        __tablename__ = 'alerts'
        id = db.Column(db.Integer, primary_key=True)
        alert_type = db.Column(db.String(50), nullable=False)
        device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=True)
        description = db.Column(db.Text)
        severity = db.Column(db.String(20), default='MEDIUM')
        timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        acknowledged = db.Column(db.Boolean, default=False)
        
        def to_dict(self):
            device = Device.query.get(self.device_id) if self.device_id else None
            return {
                'id': self.id,
                'alert_type': self.alert_type,
                'device_id': self.device_id,
                'device_ip': device.ip_address if device else None,
                'description': self.description,
                'severity': self.severity,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None,
                'acknowledged': self.acknowledged
            }
    
    # Create tables (with drop if needed)
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    # ============ ROUTES ============
    
    @app.route('/')
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'NetSentry Backend', 'version': '1.0.0'})
    
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
            online_devices = Device.query.filter_by(status='ONLINE').count()
            offline_devices = Device.query.filter_by(status='OFFLINE').count()
            open_ports = PortScan.query.filter_by(status='OPEN').count()
            latest_traffic = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).first()
            unacknowledged_alerts = Alert.query.filter_by(acknowledged=False).count()
            
            return jsonify({
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': offline_devices,
                'open_ports': open_ports,
                'latest_traffic': latest_traffic.to_dict() if latest_traffic else None,
                'unacknowledged_alerts': unacknowledged_alerts
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/devices')
    def get_devices():
        try:
            devices = Device.query.order_by(Device.last_seen.desc()).all()
            return jsonify({
                'devices': [d.to_dict() for d in devices],
                'count': len(devices)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/devices/<int:device_id>')
    def get_device(device_id):
        try:
            device = Device.query.get_or_404(device_id)
            return jsonify(device.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ports')
    def get_ports():
        try:
            status = request.args.get('status')
            query = PortScan.query
            if status:
                query = query.filter_by(status=status)
            ports = query.order_by(PortScan.port.asc()).all()
            return jsonify({
                'ports': [p.to_dict() for p in ports],
                'count': len(ports)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/traffic')
    def get_traffic():
        try:
            limit = request.args.get('limit', 100, type=int)
            stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()
            return jsonify({
                'traffic': [s.to_dict() for s in stats],
                'count': len(stats)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/alerts')
    def get_alerts():
        try:
            acknowledged = request.args.get('acknowledged', 'false').lower() == 'true'
            query = Alert.query
            if not acknowledged:
                query = query.filter_by(acknowledged=False)
            alerts = query.order_by(Alert.timestamp.desc()).limit(100).all()
            alerts_list = [a.to_dict() for a in alerts]
            return jsonify({
                'alerts': alerts_list,
                'count': len(alerts_list)
            })
        except Exception as e:
            print(f"Error in /api/alerts: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': str(e), 'alerts': [], 'count': 0}), 500
    
    @app.route('/api/devices/ingest', methods=['POST'])
    def ingest_devices():
        try:
            data = request.get_json()
            if not data or 'devices' not in data:
                return jsonify({'error': 'Invalid data format'}), 400
            
            devices_data = data['devices']
            created_count = 0
            updated_count = 0
            
            for device_data in devices_data:
                ip = device_data.get('ip_address')
                mac = device_data.get('mac_address')
                if not ip or not mac:
                    continue
                
                existing = Device.query.filter_by(ip_address=ip).first()
                if existing:
                    existing.last_seen = datetime.now(timezone.utc)
                    existing.status = 'ONLINE'
                    if device_data.get('hostname'):
                        existing.hostname = device_data.get('hostname')
                    updated_count += 1
                else:
                    device = Device(
                        ip_address=ip,
                        mac_address=mac,
                        vendor=device_data.get('vendor', 'Unknown'),
                        hostname=device_data.get('hostname'),
                        status='ONLINE'
                    )
                    db.session.add(device)
                    created_count += 1
            
            db.session.commit()
            return jsonify({
                'status': 'success',
                'created': created_count,
                'updated': updated_count,
                'total': len(devices_data)
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
