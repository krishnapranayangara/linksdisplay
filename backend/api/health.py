"""
Health check endpoints for API monitoring.
"""

from flask import Blueprint, jsonify
from datetime import datetime
import psutil
import os

health_bp = Blueprint('health', __name__, url_prefix='/api')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring API status.
    
    Returns:
        JSON response with API status and system information
    """
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            'status': 'OK',
            'message': 'Link Organizer API is running',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'uptime': psutil.boot_time()
            }
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': 'Health check failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint for basic connectivity testing.
    
    Returns:
        JSON response with pong message
    """
    return jsonify({
        'message': 'pong',
        'timestamp': datetime.utcnow().isoformat()
    }), 200 