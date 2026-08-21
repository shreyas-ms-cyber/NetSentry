"""
API Routes Blueprint
"""

from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Device, PortScan, TrafficStat, Alert

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
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

@api_bp.route('/traffic')
def get_traffic():
    try:
        stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(100).all()
        return jsonify({
            'traffic': [s.to_dict() for s in stats],
            'count': len(stats)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alerts')
def get_alerts():
    try:
        alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(100).all()
        return jsonify({
            'alerts': [a.to_dict() for a in alerts],
            'count': len(alerts)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
