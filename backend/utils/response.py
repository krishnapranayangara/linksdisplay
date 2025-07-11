"""
Response utility functions for consistent API responses.
"""
from flask import jsonify
from typing import Any, Optional


def success_response(data: Any, message: str = "Success", status_code: int = 200):
    """
    Create a standardized success response.
    
    Args:
        data: The response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Flask response with success format
    """
    return jsonify({
        'success': True,
        'data': data,
        'message': message
    }), status_code


def error_response(status_code: int, message: str, error: Optional[str] = None):
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        error: Optional error details
        
    Returns:
        Flask response with error format
    """
    response = {
        'success': False,
        'message': message
    }
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code 