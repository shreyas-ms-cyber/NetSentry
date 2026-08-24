"""
Traffic Routes
"""

from flask import jsonify, request
from app.routes import api_bp
from app.models import TrafficStat

@api_bp.route('/traffic')
def get_traffic():
    """Get traffic statistics with protocol breakdown and top talkers"""
    limit = request.args.get('limit', 100, type=int)
    stats = TrafficStat.query.order_by(TrafficStat.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'traffic': [s.to_dict() for s in stats],
        'count': len(stats)
    })
