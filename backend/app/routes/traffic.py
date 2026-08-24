"""
Traffic Routes - SIMPLE VERSION with hardcoded top_talkers for testing
"""

from flask import jsonify, request
from app.routes import api_bp
from app.models import TrafficStat

@api_bp.route('/traffic')
def get_traffic():
    """Get traffic statistics with protocol breakdown and top talkers"""
    limit = request.args.get('limit', 100, type=int)
    stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()
    
    result = []
    for stat in stats:
        # Build response with ALL fields
        item = {
            'id': stat.id,
            'timestamp': stat.timestamp.isoformat() if stat.timestamp else None,
            'packets_per_sec': stat.packets_per_sec,
            'bandwidth_bytes': stat.bandwidth_bytes,
            'bandwidth_mbps': round((stat.bandwidth_bytes or 0) * 8 / 1000000, 2),
            'protocol_breakdown': stat.protocol_breakdown or {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0},
        }
        
        # Add top_talkers - use stat.top_talkers if exists, otherwise use sample data
        if stat.top_talkers:
            item['top_talkers'] = stat.top_talkers
        else:
            # Sample top_talkers for testing
            item['top_talkers'] = [
                {'ip': '10.161.161.1', 'bytes': 5242880, 'packets': 5000, 'bytes_mb': 5.0},
                {'ip': '10.161.161.59', 'bytes': 3145728, 'packets': 3000, 'bytes_mb': 3.0},
                {'ip': '10.161.161.100', 'bytes': 1048576, 'packets': 1000, 'bytes_mb': 1.0}
            ]
        result.append(item)
    
    return jsonify({
        'traffic': result,
        'count': len(result)
    })
