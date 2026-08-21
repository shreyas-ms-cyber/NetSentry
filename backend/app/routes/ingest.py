"""
Device Ingestion Routes - Protected by X-Agent-Key
"""

from flask import request, jsonify
from app.extensions import db
from app.routes import api_bp
from app.models import Device
from datetime import datetime, timezone

@api_bp.route('/devices/ingest', methods=['POST'])
def ingest_devices():
    """Ingest discovered devices from agent"""
    data = request.get_json()
    
    if not data or 'devices' not in data:
        return jsonify({'error': 'Invalid data format'}), 400
    
    devices_data = data['devices']
    created_count = 0
    updated_count = 0
    errors = []
    
    for device_data in devices_data:
        ip = device_data.get('ip_address')
        mac = device_data.get('mac_address')
        
        if not ip or not mac:
            errors.append(f"Missing IP or MAC for device: {device_data}")
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
        'errors': errors,
        'total': len(devices_data)
    }), 200
