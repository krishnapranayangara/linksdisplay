"""
API routes for error logging operations.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError as MarshmallowValidationError

from services.error_service import ErrorService
from schemas.error_schema import ErrorSchema, ErrorListSchema, ErrorFilterSchema
from exceptions import DatabaseError, ValidationError
from utils.response import success_response, error_response

# Create blueprint
errors_bp = Blueprint('errors', __name__, url_prefix='/api/errors')

# Initialize schemas
error_schema = ErrorSchema()
error_list_schema = ErrorListSchema()
error_filter_schema = ErrorFilterSchema()


@errors_bp.route('/', methods=['GET'])
def get_errors():
    """
    Get paginated list of error logs with optional filtering.
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 50, max: 100)
        method (str): Filter by HTTP method
        endpoint (str): Filter by endpoint path
        status_code (int): Filter by status code
        error_type (str): Filter by error type
        start_date (str): Filter by start date (ISO format)
        end_date (str): Filter by end date (ISO format)
    
    Returns:
        JSON response with error logs and pagination info
    """
    try:
        # Validate and parse query parameters
        args = error_filter_schema.load(request.args)
        
        # Parse date strings if provided
        start_date = None
        end_date = None
        if args.get('start_date'):
            start_date = datetime.fromisoformat(args['start_date'].replace('Z', '+00:00'))
        if args.get('end_date'):
            end_date = datetime.fromisoformat(args['end_date'].replace('Z', '+00:00'))
        
        # Get error logs
        result = ErrorService.get_errors(
            page=args.get('page', 1),
            per_page=args.get('per_page', 50),
            method=args.get('method'),
            endpoint=args.get('endpoint'),
            status_code=args.get('status_code'),
            error_type=args.get('error_type'),
            start_date=start_date,
            end_date=end_date
        )
        
        # Serialize response
        response_data = {
            'errors': [error_schema.dump(error) for error in result['errors']],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages'],
            'has_next': result['has_next'],
            'has_prev': result['has_prev']
        }
        
        return success_response(response_data, "Error logs retrieved successfully")
        
    except MarshmallowValidationError as e:
        return error_response(400, f"Validation error: {str(e)}")
    except DatabaseError as e:
        return error_response(500, str(e))
    except Exception as e:
        return error_response(500, f"Internal server error: {str(e)}")


@errors_bp.route('/<int:error_id>', methods=['GET'])
def get_error(error_id):
    """
    Get a specific error log by ID.
    
    Args:
        error_id (int): Error log ID
    
    Returns:
        JSON response with error log details
    """
    try:
        error_log = ErrorService.get_error_by_id(error_id)
        
        if not error_log:
            return error_response(404, "Error log not found")
        
        return success_response(
            error_schema.dump(error_log),
            "Error log retrieved successfully"
        )
        
    except DatabaseError as e:
        return error_response(500, str(e))
    except Exception as e:
        return error_response(500, f"Internal server error: {str(e)}")


@errors_bp.route('/statistics', methods=['GET'])
def get_error_statistics():
    """
    Get error statistics for monitoring and analytics.
    
    Query Parameters:
        start_date (str): Start date for statistics (ISO format)
        end_date (str): End date for statistics (ISO format)
    
    Returns:
        JSON response with error statistics
    """
    try:
        # Parse date parameters
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(
                request.args['start_date'].replace('Z', '+00:00')
            )
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(
                request.args['end_date'].replace('Z', '+00:00')
            )
        
        # Get statistics
        stats = ErrorService.get_error_statistics(start_date, end_date)
        
        return success_response(stats, "Error statistics retrieved successfully")
        
    except ValueError as e:
        return error_response(400, f"Invalid date format: {str(e)}")
    except DatabaseError as e:
        return error_response(500, str(e))
    except Exception as e:
        return error_response(500, f"Internal server error: {str(e)}")


@errors_bp.route('/cleanup', methods=['DELETE'])
def cleanup_old_errors():
    """
    Delete error logs older than specified days.
    
    Query Parameters:
        days (int): Number of days to keep (default: 30)
    
    Returns:
        JSON response with cleanup results
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1:
            return error_response(400, "Days must be at least 1")
        
        deleted_count = ErrorService.delete_old_errors(days)
        
        return success_response(
            {'deleted_count': deleted_count, 'days_kept': days},
            f"Successfully deleted {deleted_count} old error logs"
        )
        
    except DatabaseError as e:
        return error_response(500, str(e))
    except Exception as e:
        return error_response(500, f"Internal server error: {str(e)}")


@errors_bp.route('/export', methods=['GET'])
def export_errors():
    """
    Export error logs as JSON or CSV.
    
    Query Parameters:
        format (str): Export format ('json' or 'csv', default: 'json')
        start_date (str): Start date for export (ISO format)
        end_date (str): End date for export (ISO format)
        limit (int): Maximum number of records to export (default: 1000)
    
    Returns:
        File download or JSON response with exported data
    """
    try:
        export_format = request.args.get('format', 'json').lower()
        limit = min(request.args.get('limit', 1000, type=int), 10000)  # Max 10k records
        
        # Parse date parameters
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(
                request.args['start_date'].replace('Z', '+00:00')
            )
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(
                request.args['end_date'].replace('Z', '+00:00')
            )
        
        # Get error logs (no pagination for export)
        result = ErrorService.get_errors(
            page=1,
            per_page=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        if export_format == 'csv':
            # TODO: Implement CSV export
            return error_response(501, "CSV export not yet implemented")
        else:
            # JSON export
            export_data = {
                'export_info': {
                    'format': 'json',
                    'total_records': len(result['errors']),
                    'export_date': datetime.utcnow().isoformat(),
                    'date_range': {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None
                    }
                },
                'errors': [error_schema.dump(error) for error in result['errors']]
            }
            
            return success_response(export_data, "Error logs exported successfully")
        
    except ValueError as e:
        return error_response(400, f"Invalid date format: {str(e)}")
    except DatabaseError as e:
        return error_response(500, str(e))
    except Exception as e:
        return error_response(500, f"Internal server error: {str(e)}") 