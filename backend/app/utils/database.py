"""
Database utility functions
"""

from app import db
from app.models import Device, PortScan, TrafficStat, Alert

def get_device_by_ip(ip_address):
    """Get device by IP address"""
    return Device.query.filter_by(ip_address=ip_address).first()

def get_device_by_mac(mac_address):
    """Get device by MAC address"""
    return Device.query.filter_by(mac_address=mac_address).first()

def get_device_with_ports(device_id):
    """Get device with its port scans"""
    return Device.query.filter_by(id=device_id).first()

def get_recent_traffic(limit=100):
    """Get recent traffic statistics"""
    return TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()

def get_recent_alerts(limit=50, acknowledged=False):
    """Get recent alerts"""
    query = Alert.query.order_by(Alert.timestamp.desc())
    if not acknowledged:
        query = query.filter_by(acknowledged=False)
    return query.limit(limit).all()

def get_open_ports(device_id=None):
    """Get open ports, optionally filtered by device"""
    query = PortScan.query.filter_by(status='OPEN')
    if device_id:
        query = query.filter_by(device_id=device_id)
    return query.all()

def get_device_status_counts():
    """Get counts of devices by status"""
    online = Device.query.filter_by(status='ONLINE').count()
    offline = Device.query.filter_by(status='OFFLINE').count()
    return {'online': online, 'offline': offline, 'total': online + offline}
