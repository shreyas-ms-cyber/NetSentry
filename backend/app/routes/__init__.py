"""
API Routes Blueprint - All routes in one file
"""

from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Device, PortScan, TrafficStat, Alert
from datetime import datetime, timezone
import traceback
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# ============== HEALTH ==============
@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'NetSentry API'})

# ============== DEVICE ROUTES ==============
@api_bp.route('/devices', methods=['GET'])
def get_devices():
    try:
        devices = Device.query.order_by(Device.last_seen.desc()).all()
        return jsonify({
            'devices': [d.to_dict() for d in devices],
            'count': len(devices)
        })
    except Exception as e:
        logger.error(f"Error in /devices: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        return jsonify(device.to_dict())
    except Exception as e:
        logger.error(f"Error in /devices/{device_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/devices/<int:device_id>/ports', methods=['GET'])
def get_device_ports(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        ports = device.port_scans.order_by(PortScan.scanned_at.desc()).all()
        return jsonify({
            'device': device.to_dict(),
            'ports': [p.to_dict() for p in ports],
            'count': len(ports)
        })
    except Exception as e:
        logger.error(f"Error in /devices/{device_id}/ports: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============== DEVICE INGESTION ==============
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
        logger.error(f"Error in /devices/ingest: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ============== PORT ROUTES ==============
@api_bp.route('/ports', methods=['GET'])
def get_ports():
    try:
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
        return jsonify({
            'ports': [p.to_dict() for p in ports],
            'count': len(ports)
        })
    except Exception as e:
        logger.error(f"Error in /ports: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ports/ingest', methods=['POST'])
def ingest_port_scans():
    try:
        data = request.get_json()
        if not data or 'port_scans' not in data:
            return jsonify({'error': 'Invalid data format'}), 400
        
        port_scans_data = data['port_scans']
        created_count = 0
        
        for scan_data in port_scans_data:
            device_ip = scan_data.get('device_ip') or scan_data.get('ip_address')
            if not device_ip:
                continue
            
            device = Device.query.filter_by(ip_address=device_ip).first()
            if not device:
                continue
            
            port = scan_data.get('port')
            protocol = scan_data.get('protocol', 'TCP')
            status = scan_data.get('status', 'CLOSED')
            scanned_at_str = scan_data.get('scanned_at')
            
            if not port:
                continue
            
            scanned_at = datetime.fromisoformat(scanned_at_str) if scanned_at_str else datetime.now(timezone.utc)
            
            port_scan = PortScan(
                device_id=device.id,
                port=port,
                protocol=protocol,
                status=status,
                scanned_at=scanned_at
            )
            db.session.add(port_scan)
            created_count += 1
        
        db.session.commit()
        return jsonify({
            'status': 'success',
            'created': created_count,
            'total': len(port_scans_data)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in /ports/ingest: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============== TRAFFIC ROUTES ==============
@api_bp.route('/traffic', methods=['GET'])
def get_traffic():
    try:
        limit = request.args.get('limit', 100, type=int)
        stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()
        return jsonify({
            'traffic': [s.to_dict() for s in stats],
            'count': len(stats)
        })
    except Exception as e:
        logger.error(f"Error in /traffic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/traffic/ingest', methods=['POST'])
def ingest_traffic():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid data format'}), 400
        
        timestamp_str = data.get('timestamp')
        packets_per_sec = data.get('packets_per_sec', 0)
        bandwidth_bytes = data.get('bandwidth_bytes', 0)
        protocol_breakdown = data.get('protocol_breakdown', {})
        
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now(timezone.utc)
        
        traffic_stat = TrafficStat(
            timestamp=timestamp,
            packets_per_sec=packets_per_sec,
            bandwidth_bytes=bandwidth_bytes,
            protocol_breakdown=protocol_breakdown
        )
        db.session.add(traffic_stat)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Traffic stats ingested successfully',
            'id': traffic_stat.id
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in /traffic/ingest: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============== ALERT ROUTES ==============
@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    try:
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
    except Exception as e:
        logger.error(f"Error in /alerts: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    try:
        alert = Alert.query.get_or_404(alert_id)
        alert.acknowledged = True
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Alert acknowledged',
            'alert': alert.to_dict()
        })
    except Exception as e:
        logger.error(f"Error in /alerts/{alert_id}/acknowledge: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============== DASHBOARD SUMMARY ==============
@api_bp.route('/dashboard/summary', methods=['GET'])
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
        logger.error(f"Error in /dashboard/summary: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
