"""
Service layer for error logging operations.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import and_, desc
from sqlalchemy.orm import Query

from models.error import Error
from extensions import db
from exceptions import DatabaseError, ValidationError


class ErrorService:
    """
    Service class for error logging operations.
    
    This service handles all business logic related to error logging
    including creating, retrieving, and filtering error logs.
    """
    
    @staticmethod
    def log_error(
        method: str,
        endpoint: str,
        status_code: int,
        request_data: Optional[Dict] = None,
        request_params: Optional[Dict] = None,
        request_headers: Optional[Dict] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        request_time: Optional[datetime] = None,
        response_time: Optional[datetime] = None,
        duration_ms: Optional[int] = None
    ) -> Error:
        """
        Log an API call with all its details.
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            status_code: HTTP status code
            request_data: Request body data
            request_params: Query parameters
            request_headers: Request headers (will be sanitized)
            client_ip: Client IP address
            user_agent: User agent string
            response_data: Response body data
            error_message: Error message if any
            error_type: Type of error
            session_id: Session identifier
            user_id: User ID if authenticated
            request_time: Request timestamp
            response_time: Response timestamp
            duration_ms: Request duration in milliseconds
            
        Returns:
            Error: The created error log entry
            
        Raises:
            ValidationError: If required fields are missing or invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate required fields
            if not method or not endpoint or not status_code:
                raise ValidationError("Method, endpoint, and status_code are required")
            
            # Sanitize headers (remove sensitive information)
            sanitized_headers = None
            if request_headers:
                sanitized_headers = {
                    k: v for k, v in request_headers.items()
                    if k.lower() not in ['authorization', 'cookie', 'x-api-key']
                }
            
            # Create error log entry
            error_log = Error(
                method=method.upper(),
                endpoint=endpoint,
                status_code=status_code,
                request_data=request_data,
                request_params=request_params,
                request_headers=sanitized_headers,
                client_ip=client_ip,
                user_agent=user_agent,
                response_data=response_data,
                error_message=error_message,
                error_type=error_type,
                session_id=session_id,
                user_id=user_id,
                request_time=request_time or datetime.utcnow(),
                response_time=response_time,
                duration_ms=duration_ms
            )
            
            db.session.add(error_log)
            db.session.commit()
            
            return error_log
            
        except ValidationError:
            raise
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to log error: {str(e)}")
    
    @staticmethod
    def get_error_by_id(error_id: int) -> Optional[Error]:
        """
        Get error log by ID.
        
        Args:
            error_id: Error log ID
            
        Returns:
            Error: Error log entry or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Error.query.get(error_id)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve error log: {str(e)}")
    
    @staticmethod
    def get_errors(
        page: int = 1,
        per_page: int = 50,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        error_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of error logs with optional filtering.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            method: Filter by HTTP method
            endpoint: Filter by endpoint path
            status_code: Filter by status code
            error_type: Filter by error type
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Dict containing errors, total count, and pagination info
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = Error.query
            
            # Apply filters
            if method:
                query = query.filter(Error.method == method.upper())
            if endpoint:
                query = query.filter(Error.endpoint.contains(endpoint))
            if status_code:
                query = query.filter(Error.status_code == status_code)
            if error_type:
                query = query.filter(Error.error_type == error_type)
            if start_date:
                query = query.filter(Error.request_time >= start_date)
            if end_date:
                query = query.filter(Error.request_time <= end_date)
            
            # Order by most recent first
            query = query.order_by(desc(Error.request_time))
            
            # Paginate
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'errors': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve error logs: {str(e)}")
    
    @staticmethod
    def get_error_statistics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get error statistics for monitoring and analytics.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dict containing various error statistics
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = Error.query
            
            if start_date:
                query = query.filter(Error.request_time >= start_date)
            if end_date:
                query = query.filter(Error.request_time <= end_date)
            
            # Get total count
            total_requests = query.count()
            
            # Get error counts by status code
            error_counts = db.session.query(
                Error.status_code,
                db.func.count(Error.id).label('count')
            ).filter(query.whereclause).group_by(Error.status_code).all()
            
            # Get error counts by method
            method_counts = db.session.query(
                Error.method,
                db.func.count(Error.id).label('count')
            ).filter(query.whereclause).group_by(Error.method).all()
            
            # Get error counts by endpoint
            endpoint_counts = db.session.query(
                Error.endpoint,
                db.func.count(Error.id).label('count')
            ).filter(query.whereclause).group_by(Error.endpoint).order_by(
                db.func.count(Error.id).desc()
            ).limit(10).all()
            
            # Get average response time
            avg_duration = db.session.query(
                db.func.avg(Error.duration_ms)
            ).filter(query.whereclause).scalar()
            
            return {
                'total_requests': total_requests,
                'status_code_counts': {str(code): count for code, count in error_counts},
                'method_counts': {method: count for method, count in method_counts},
                'top_endpoints': {endpoint: count for endpoint, count in endpoint_counts},
                'average_response_time_ms': float(avg_duration) if avg_duration else 0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve error statistics: {str(e)}")
    
    @staticmethod
    def delete_old_errors(days: int = 30) -> int:
        """
        Delete error logs older than specified days.
        
        Args:
            days: Number of days to keep (default: 30)
            
        Returns:
            int: Number of deleted records
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = Error.query.filter(
                Error.request_time < cutoff_date
            ).delete()
            
            db.session.commit()
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete old error logs: {str(e)}") 