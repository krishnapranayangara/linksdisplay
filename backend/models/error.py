"""
Error model for logging API calls and responses.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from extensions import db


class Error(db.Model):
    """
    Error model for logging API calls and their responses.
    
    This table stores comprehensive information about all API requests
    including request details, response status, error messages, and timing.
    """
    __tablename__ = 'errors'
    
    id = Column(Integer, primary_key=True)
    
    # Request information
    method = Column(String(10), nullable=False, comment='HTTP method (GET, POST, PUT, DELETE)')
    endpoint = Column(String(255), nullable=False, comment='API endpoint path')
    request_data = Column(JSON, nullable=True, comment='Request body data (for POST/PUT)')
    request_params = Column(JSON, nullable=True, comment='Query parameters')
    request_headers = Column(JSON, nullable=True, comment='Request headers (sanitized)')
    client_ip = Column(String(45), nullable=True, comment='Client IP address')
    user_agent = Column(String(500), nullable=True, comment='User agent string')
    
    # Response information
    status_code = Column(Integer, nullable=False, comment='HTTP status code')
    response_data = Column(JSON, nullable=True, comment='Response body data')
    error_message = Column(Text, nullable=True, comment='Error message if any')
    error_type = Column(String(100), nullable=True, comment='Type of error (ValidationError, DatabaseError, etc.)')
    
    # Timing information
    request_time = Column(DateTime, nullable=False, default=func.now(), comment='Timestamp when request was received')
    response_time = Column(DateTime, nullable=True, comment='Timestamp when response was sent')
    duration_ms = Column(Integer, nullable=True, comment='Request duration in milliseconds')
    
    # Additional context
    session_id = Column(String(100), nullable=True, comment='Session identifier if available')
    user_id = Column(Integer, nullable=True, comment='User ID if authenticated')
    
    def __repr__(self):
        return f'<Error {self.method} {self.endpoint} {self.status_code}>'
    
    def to_dict(self):
        """Convert error log to dictionary."""
        return {
            'id': self.id,
            'method': self.method,
            'endpoint': self.endpoint,
            'request_data': self.request_data,
            'request_params': self.request_params,
            'request_headers': self.request_headers,
            'client_ip': self.client_ip,
            'user_agent': self.user_agent,
            'status_code': self.status_code,
            'response_data': self.response_data,
            'error_message': self.error_message,
            'error_type': self.error_type,
            'request_time': self.request_time.isoformat() if self.request_time else None,
            'response_time': self.response_time.isoformat() if self.response_time else None,
            'duration_ms': self.duration_ms,
            'session_id': self.session_id,
            'user_id': self.user_id
        } 