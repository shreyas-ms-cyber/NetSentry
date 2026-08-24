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
    protocol_breakdown = db.Column(db.JSON)  # JSON: {tcp: 45, udp: 30, icmp: 15, other: 10}
    top_talkers = db.Column(db.JSON)  # JSON: [{'ip': '192.168.1.10', 'bytes': 1024, 'packets': 100}]
    
    __table_args__ = (
        db.Index('idx_timestamp', 'timestamp'),
    )
    
    def to_dict(self):
        """Convert traffic stat to dictionary for API responses"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'packets_per_sec': self.packets_per_sec,
            'bandwidth_bytes': self.bandwidth_bytes,
            'bandwidth_mbps': round((self.bandwidth_bytes or 0) * 8 / 1000000, 2),
            'protocol_breakdown': self.protocol_breakdown or {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0},
            'top_talkers': self.top_talkers or []
        }
    
    def __repr__(self):
        return f'<TrafficStat {self.timestamp} - {self.packets_per_sec} pps>'
