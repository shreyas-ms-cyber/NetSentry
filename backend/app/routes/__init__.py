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
from app.routes import traffic  # Use the updated traffic route

@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'NetSentry API'})

@api_bp.route('/devices')
def get_devices():
    devices = Device.query.order_by(Device.last_seen.desc()).all()
    result = []
    for device in devices:
        device_dict = device.to_dict()
        open_ports = PortScan.query.filter_by(device_id=device.id, status='OPEN').count()
        device_dict['open_ports_count'] = open_ports
        result.append(device_dict)
    return jsonify({'devices': result, 'count': len(result)})

@api_bp.route('/devices/<int:device_id>')
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    device_dict = device.to_dict()
    open_ports = PortScan.query.filter_by(device_id=device.id, status='OPEN').count()
    device_dict['open_ports_count'] = open_ports
    return jsonify(device_dict)

@api_bp.route('/devices/<int:device_id>/ports')
def get_device_ports(device_id):
    device = Device.query.get_or_404(device_id)
    ports = PortScan.query.filter_by(device_id=device_id).order_by(PortScan.port.asc()).all()
    return jsonify({
        'device': device.to_dict(),
        'ports': [p.to_dict() for p in ports],
        'count': len(ports)
    })

@api_bp.route('/ports')
def get_ports():
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
    
    ports = query.order_by(PortScan.port.asc()).all()
    return jsonify({'ports': [p.to_dict() for p in ports], 'count': len(ports)})

@api_bp.route('/alerts')
def get_alerts():
    acknowledged = request.args.get('acknowledged', 'false').lower() == 'true'
    severity = request.args.get('severity')
    
    query = Alert.query
    if not acknowledged:
        query = query.filter_by(acknowledged=False)
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(100).all()
    return jsonify({'alerts': [a.to_dict() for a in alerts], 'count': len(alerts)})

@api_bp.route('/dashboard/summary')
def dashboard_summary():
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

@api_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.acknowledged = True
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': 'Alert acknowledged',
        'alert': alert.to_dict()
    })
