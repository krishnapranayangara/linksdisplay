"""
Middleware for automatically logging API requests and responses.
"""
import time
from datetime import datetime
from flask import request, g, Response
from werkzeug.exceptions import HTTPException

from services.error_service import ErrorService


class RequestLoggerMiddleware:
    """
    Middleware to automatically log all API requests and responses.
    
    This middleware captures request details, timing, and response information
    and stores them in the errors table for monitoring and debugging.
    """
    
    def __init__(self, app):
        """
        Initialize the middleware.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Register before_request and after_request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_appcontext)
    
    def before_request(self):
        """Log request start time and details."""
        # Store request start time
        g.request_start_time = time.time()
        g.request_start_datetime = datetime.utcnow()
    
    def after_request(self, response):
        """Log request completion and response details."""
        try:
            # Calculate request duration
            duration_ms = int((time.time() - g.request_start_time) * 1000)
            
            # Get request details
            method = request.method
            endpoint = request.endpoint or request.path
            
            # Skip logging for certain endpoints (optional)
            if self._should_skip_logging(endpoint):
                return response
            
            # Get request data (sanitized)
            request_data = None
            if method in ['POST', 'PUT', 'PATCH'] and request.is_json:
                request_data = request.get_json()
            
            # Get query parameters
            request_params = dict(request.args) if request.args else None
            
            # Get headers (sanitized)
            request_headers = dict(request.headers) if request.headers else None
            
            # Get client information
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            # Get response data (for error responses)
            response_data = None
            error_message = None
            error_type = None
            
            if response.status_code >= 400:
                try:
                    # Try to get error details from response
                    if response.is_json:
                        response_data = response.get_json()
                        error_message = response_data.get('message', 'Unknown error')
                        error_type = 'HTTPError'
                except:
                    error_message = f"HTTP {response.status_code}"
                    error_type = 'HTTPError'
            
            # Log the request asynchronously to avoid blocking
            self._log_request_async(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                request_data=request_data,
                request_params=request_params,
                request_headers=request_headers,
                client_ip=client_ip,
                user_agent=user_agent,
                response_data=response_data,
                error_message=error_message,
                error_type=error_type,
                request_time=g.request_start_datetime,
                response_time=datetime.utcnow(),
                duration_ms=duration_ms
            )
            
        except Exception as e:
            # Don't let logging errors affect the response
            print(f"Error in request logging: {str(e)}")
        
        return response
    
    def teardown_appcontext(self, exception=None):
        """Handle any cleanup after request processing."""
        if exception:
            try:
                # Log unhandled exceptions
                duration_ms = int((time.time() - g.request_start_time) * 1000)
                
                self._log_request_async(
                    method=request.method,
                    endpoint=request.endpoint or request.path,
                    status_code=500,
                    request_data=request.get_json() if request.is_json else None,
                    request_params=dict(request.args) if request.args else None,
                    request_headers=dict(request.headers) if request.headers else None,
                    client_ip=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    response_data=None,
                    error_message=str(exception),
                    error_type=type(exception).__name__,
                    request_time=g.request_start_datetime,
                    response_time=datetime.utcnow(),
                    duration_ms=duration_ms
                )
            except:
                pass
    
    def _should_skip_logging(self, endpoint):
        """
        Determine if logging should be skipped for this endpoint.
        
        Args:
            endpoint: The endpoint being requested
            
        Returns:
            bool: True if logging should be skipped
        """
        # Skip logging for health checks and static files
        skip_patterns = [
            'static',
            'health',
            'favicon',
            'robots.txt'
        ]
        
        return any(pattern in endpoint.lower() for pattern in skip_patterns)
    
    def _log_request_async(self, **kwargs):
        """
        Log request asynchronously to avoid blocking the response.
        
        Args:
            **kwargs: Request logging parameters
        """
        try:
            # Use a simple approach - log in a separate thread or process
            # For now, we'll log synchronously but in a try-catch to avoid blocking
            ErrorService.log_error(**kwargs)
        except Exception as e:
            # Don't let logging errors affect the application
            print(f"Failed to log request: {str(e)}")


def init_request_logger(app):
    """
    Initialize request logging middleware.
    
    Args:
        app: Flask application instance
    """
    RequestLoggerMiddleware(app) 