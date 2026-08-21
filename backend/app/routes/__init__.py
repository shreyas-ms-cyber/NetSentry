"""
API Routes Blueprint
"""

from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Device, PortScan, TrafficStat, Alert
from datetime import datetime, timezone
import traceback

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'NetSentry API'})

@api_bp.route('/devices')
def get_devices():
    try:
        devices = Device.query.all()
        return jsonify({
            'devices': [d.to_dict() for d in devices],
            'count': len(devices)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@api_bp.route('/devices/ingest', methods=['POST'])
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
                if device_data.get('vendor') and device_data.get('vendor') != 'Unknown Vendor':
                    existing.vendor = device_data.get('vendor')
                updated_count += 1
            else:
                device = Device(
                    ip_address=ip,
                    mac_address=mac,
                    vendor=device_data.get('vendor', 'Unknown'),
                    hostname=device_data.get('hostname'),
                    status='ONLINE',
                    first_seen=datetime.now(timezone.utc),
                    last_seen=datetime.now(timezone.utc)
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
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@api_bp.route('/dashboard/summary')
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
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@api_bp.route('/traffic')
def get_traffic():
    try:
        stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(100).all()
        return jsonify({
            'traffic': [s.to_dict() for s in stats],
            'count': len(stats)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@api_bp.route('/alerts')
def get_alerts():
    try:
        alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(100).all()
        return jsonify({
            'alerts': [a.to_dict() for a in alerts],
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@api_bp.route('/ports')
def get_ports():
    try:
        ports = PortScan.query.all()
        return jsonify({
            'ports': [p.to_dict() for p in ports],
            'count': len(ports)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
