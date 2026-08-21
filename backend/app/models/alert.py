"""
Alert Model - Represents security alerts from network monitoring
"""

from datetime import datetime
from app.extensions import db

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # NEW_DEVICE, NEW_OPEN_PORT, DEVICE_OFFLINE
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=True, index=True)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='MEDIUM')  # LOW, MEDIUM, HIGH
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    acknowledged = db.Column(db.Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_timestamp_desc', 'timestamp', 'acknowledged'),
        db.Index('idx_alert_type', 'alert_type'),
    )
    
    def to_dict(self):
        """Convert alert to dictionary for API responses"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'device_id': self.device_id,
            'device_ip': self.device.ip_address if self.device else None,
            'description': self.description,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'acknowledged': self.acknowledged
        }
    
    def __repr__(self):
        return f'<Alert {self.alert_type} - {self.severity}>'
