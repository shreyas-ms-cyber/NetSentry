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
    
    result = []
    for stat in stats:
        stat_dict = stat.to_dict()
        # Ensure top_talkers is included
        if 'top_talkers' not in stat_dict:
            stat_dict['top_talkers'] = stat.top_talkers or []
        result.append(stat_dict)
    
    return jsonify({
        'traffic': result,
        'count': len(result)
    })
