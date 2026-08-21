"""
Ingestion Routes - Protected by X-Agent-Key
"""

from flask import request, jsonify
from app.extensions import db
from app.routes import api_bp
from app.models import Device, PortScan, TrafficStat, Alert
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/devices/ingest', methods=['POST'])
def ingest_devices():
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
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    return jsonify({
        'status': 'success',
        'created': created_count,
        'updated': updated_count,
        'total': len(devices_data)
    }), 200

@api_bp.route('/ports/ingest', methods=['POST'])
def ingest_port_scans():
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
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    return jsonify({
        'status': 'success',
        'created': created_count,
        'total': len(port_scans_data)
    }), 200

@api_bp.route('/traffic/ingest', methods=['POST'])
def ingest_traffic():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data format'}), 400
    
    try:
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
        return jsonify({'error': f'Database error: {str(e)}'}), 500
