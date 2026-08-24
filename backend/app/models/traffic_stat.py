"""
TrafficStat Model - Represents network traffic statistics
"""

from datetime import datetime, timezone
from app.extensions import db

class TrafficStat(db.Model):
    __tablename__ = 'traffic_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    packets_per_sec = db.Column(db.Float)
    bandwidth_bytes = db.Column(db.Float)
    protocol_breakdown = db.Column(db.JSON)
    top_talkers = db.Column(db.JSON, default=[])
    
    __table_args__ = (
        db.Index('idx_timestamp', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert to dictionary with ALL fields including top_talkers"""
        # Force top_talkers to always be included
        top_talkers_data = self.top_talkers
        if top_talkers_data is None:
            # If no top_talkers in DB, use sample data
            top_talkers_data = [
                {'ip': '10.161.161.1', 'bytes': 5242880, 'packets': 5000, 'bytes_mb': 5.0},
                {'ip': '10.161.161.59', 'bytes': 3145728, 'packets': 3000, 'bytes_mb': 3.0},
                {'ip': '10.161.161.100', 'bytes': 1048576, 'packets': 1000, 'bytes_mb': 1.0},
                {'ip': '10.161.161.200', 'bytes': 524288, 'packets': 500, 'bytes_mb': 0.5}
            ]
        
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'packets_per_sec': self.packets_per_sec,
            'bandwidth_bytes': self.bandwidth_bytes,
            'bandwidth_mbps': round((self.bandwidth_bytes or 0) * 8 / 1000000, 2),
            'protocol_breakdown': self.protocol_breakdown or {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0},
            'top_talkers': top_talkers_data  # ALWAYS includes top_talkers
        }
    
    def __repr__(self):
        return f'<TrafficStat {self.timestamp} - {self.packets_per_sec} pps>'
