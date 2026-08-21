"""
API Routes Blueprint
"""

from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Device, PortScan, TrafficStat, Alert
from datetime import datetime, timezone

api_bp = Blueprint('api', __name__)

# Import all route modules
from app.routes import ingest

# Health check endpoint
@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'NetSentry API'})

# Devices endpoints
@api_bp.route('/devices')
def get_devices():
    """Get all devices"""
    devices = Device.query.order_by(Device.last_seen.desc()).all()
    return jsonify({
        'devices': [d.to_dict() for d in devices],
        'count': len(devices)
    })

@api_bp.route('/devices/<int:device_id>')
def get_device(device_id):
    """Get device by ID"""
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict())

@api_bp.route('/devices/<int:device_id>/ports')
def get_device_ports(device_id):
    """Get ports for a device"""
    device = Device.query.get_or_404(device_id)
    ports = device.port_scans.order_by(PortScan.scanned_at.desc()).all()
    return jsonify({
        'device': device.to_dict(),
        'ports': [p.to_dict() for p in ports]
    })

# Ports endpoints
@api_bp.route('/ports')
def get_ports():
    """Get all ports, optionally filtered"""
    status = request.args.get('status')
    protocol = request.args.get('protocol')
    port = request.args.get('port')
    
    query = PortScan.query
    if status:
        query = query.filter_by(status=status)
    if protocol:
        query = query.filter_by(protocol=protocol)
    if port:
        query = query.filter_by(port=int(port))
    
    ports = query.order_by(PortScan.scanned_at.desc()).limit(100).all()
    return jsonify({
        'ports': [p.to_dict() for p in ports],
        'count': len(ports)
    })

# Traffic endpoints
@api_bp.route('/traffic')
def get_traffic():
    """Get traffic statistics"""
    limit = request.args.get('limit', 100, type=int)
    stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()
    return jsonify({
        'traffic': [s.to_dict() for s in stats],
        'count': len(stats)
    })

# Alerts endpoints
@api_bp.route('/alerts')
def get_alerts():
    """Get alerts, optionally filtered"""
    acknowledged = request.args.get('acknowledged', 'false').lower() == 'true'
    severity = request.args.get('severity')
    
    query = Alert.query
    if not acknowledged:
        query = query.filter_by(acknowledged=False)
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(100).all()
    return jsonify({
        'alerts': [a.to_dict() for a in alerts],
        'count': len(alerts)
    })

# Dashboard summary endpoint
@api_bp.route('/dashboard/summary')
def dashboard_summary():
    """Get dashboard summary statistics"""
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
