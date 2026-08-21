"""
API Routes Blueprint
"""

from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

# Health check endpoint
@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'NetSentry API'})

# Placeholder for future routes
@api_bp.route('/devices')
def get_devices():
    return jsonify({'devices': [], 'message': 'Phase 7 implementation'})

@api_bp.route('/ports')
def get_ports():
    return jsonify({'ports': [], 'message': 'Phase 7 implementation'})

@api_bp.route('/traffic')
def get_traffic():
    return jsonify({'traffic': [], 'message': 'Phase 7 implementation'})

@api_bp.route('/alerts')
def get_alerts():
    return jsonify({'alerts': [], 'message': 'Phase 7 implementation'})
