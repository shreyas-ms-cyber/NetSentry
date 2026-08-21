"""
PortScan Model
"""

from datetime import datetime, timezone
from app.extensions import db

class PortScan(db.Model):
    __tablename__ = 'port_scans'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)
    port = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    scanned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    __table_args__ = (
        db.Index('idx_device_port_protocol', 'device_id', 'port', 'protocol'),
        db.Index('idx_scanned_at', 'scanned_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'port': self.port,
            'protocol': self.protocol,
            'status': self.status,
            'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None
        }
    
    def __repr__(self):
        return f'<PortScan {self.port}/{self.protocol} - {self.status}>'
