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
        logger.error(f"Device ingestion error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    return jsonify({
        'status': 'success',
        'created': created_count,
        'updated': updated_count,
        'errors': errors,
        'total': len(devices_data)
    }), 200


@api_bp.route('/ports/ingest', methods=['POST'])
def ingest_port_scans():
    data = request.get_json()
    if not data or 'port_scans' not in data:
        return jsonify({'error': 'Invalid data format'}), 400
    
    port_scans_data = data['port_scans']
    created_count = 0
    errors = []
    
    for scan_data in port_scans_data:
        try:
            device_ip = scan_data.get('device_ip') or scan_data.get('ip_address')
            if not device_ip:
                errors.append(f"Missing device_ip for port scan: {scan_data}")
                continue
            
            device = Device.query.filter_by(ip_address=device_ip).first()
            if not device:
                logger.warning(f"Device not found for IP: {device_ip}")
                errors.append(f"Device not found for IP: {device_ip}")
                continue
            
            port = scan_data.get('port')
            protocol = scan_data.get('protocol', 'TCP')
            status = scan_data.get('status', 'CLOSED')
            scanned_at_str = scan_data.get('scanned_at')
            
            if not port:
                errors.append(f"Missing port for scan: {scan_data}")
                continue
            
            if scanned_at_str:
                try:
                    scanned_at = datetime.fromisoformat(scanned_at_str)
                except ValueError:
                    scanned_at = datetime.now(timezone.utc)
            else:
                scanned_at = datetime.now(timezone.utc)
            
            existing = PortScan.query.filter_by(
                device_id=device.id,
                port=port,
                protocol=protocol
            ).order_by(PortScan.scanned_at.desc()).first()
            
            if existing:
                existing.status = status
                existing.scanned_at = scanned_at
            else:
                port_scan = PortScan(
                    device_id=device.id,
                    port=port,
                    protocol=protocol,
                    status=status,
                    scanned_at=scanned_at
                )
                db.session.add(port_scan)
            
            created_count += 1
            
        except Exception as e:
            logger.error(f"Error processing port scan: {e}")
            errors.append(f"Error: {str(e)}")
            continue
    
    try:
        db.session.commit()
        logger.info(f"✅ Successfully saved {created_count} port scans")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Port scan ingestion error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    return jsonify({
        'status': 'success',
        'created': created_count,
        'errors': errors,
        'total': len(port_scans_data)
    }), 200


@api_bp.route('/traffic/ingest', methods=['POST'])
def ingest_traffic():
    """Ingest traffic statistics from agent"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data format'}), 400
    
    try:
        timestamp_str = data.get('timestamp')
        packets_per_sec = data.get('packets_per_sec', 0)
        bandwidth_bytes = data.get('bandwidth_bytes', 0)
        protocol_breakdown = data.get('protocol_breakdown', {})
        total_packets = data.get('total_packets', 0)
        top_talkers = data.get('top_talkers', [])
        
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)
        
        traffic_stat = TrafficStat(
            timestamp=timestamp,
            packets_per_sec=packets_per_sec,
            bandwidth_bytes=bandwidth_bytes,
            protocol_breakdown=protocol_breakdown,
            top_talkers=top_talkers  # Store top_talkers
        )
        
        db.session.add(traffic_stat)
        db.session.commit()
        
        logger.info(f"✅ Traffic stats saved: {packets_per_sec:.2f} pps, {bandwidth_bytes:.2f} B/s")
        
        return jsonify({
            'status': 'success',
            'message': 'Traffic stats ingested successfully',
            'id': traffic_stat.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Traffic ingestion error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
