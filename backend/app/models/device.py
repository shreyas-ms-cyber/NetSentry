"""
Device Model - Represents network devices discovered on the local network
"""

from datetime import datetime, timezone
from app.extensions import db

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    mac_address = db.Column(db.String(17), nullable=False, index=True)
    vendor = db.Column(db.String(100))
    hostname = db.Column(db.String(255))
    first_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='ONLINE')
    
    port_scans = db.relationship('PortScan', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        from app.models import PortScan
        open_ports_count = PortScan.query.filter_by(device_id=self.id, status='OPEN').count()
        
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'vendor': self.vendor,
            'hostname': self.hostname,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'status': self.status,
            'open_ports_count': open_ports_count
        }
    
    def __repr__(self):
        return f'<Device {self.ip_address} ({self.hostname or "Unknown"})>'
