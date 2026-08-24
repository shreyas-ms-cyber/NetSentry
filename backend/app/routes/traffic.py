"""
Traffic Routes - FINAL VERSION with guaranteed top_talkers
"""

from flask import jsonify, request
from app.routes import api_bp
from app.models import TrafficStat

@api_bp.route('/traffic')
def get_traffic():
    limit = request.args.get('limit', 100, type=int)
    stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()
    
    result = []
    for stat in stats:
        # Build response manually to ensure top_talkers is included
        item = {
            'id': stat.id,
            'timestamp': stat.timestamp.isoformat() if stat.timestamp else None,
            'packets_per_sec': stat.packets_per_sec,
            'bandwidth_bytes': stat.bandwidth_bytes,
            'bandwidth_mbps': round((stat.bandwidth_bytes or 0) * 8 / 1000000, 2),
            'protocol_breakdown': stat.protocol_breakdown or {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0},
            'top_talkers': stat.top_talkers or []
        }
        result.append(item)
    
    return jsonify({'traffic': result, 'count': len(result)})
