"""
Tests for error logging functionality.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from models.error import Error
from services.error_service import ErrorService
from extensions import db


class TestErrorModel:
    """Test cases for Error model."""
    
    def test_error_creation(self, app):
        """Test creating an error log entry."""
        with app.app_context():
            error = Error(
                method='GET',
                endpoint='/api/test',
                status_code=200,
                request_data={'test': 'data'},
                client_ip='127.0.0.1',
                user_agent='test-agent'
            )
            
            db.session.add(error)
            db.session.commit()
            
            assert error.id is not None
            assert error.method == 'GET'
            assert error.endpoint == '/api/test'
            assert error.status_code == 200
            assert error.request_data == {'test': 'data'}
            assert error.client_ip == '127.0.0.1'
            assert error.user_agent == 'test-agent'
    
    def test_error_to_dict(self, app):
        """Test converting error to dictionary."""
        with app.app_context():
            error = Error(
                method='POST',
                endpoint='/api/test',
                status_code=400,
                error_message='Test error',
                error_type='ValidationError'
            )
            
            error_dict = error.to_dict()
            
            assert error_dict['method'] == 'POST'
            assert error_dict['endpoint'] == '/api/test'
            assert error_dict['status_code'] == 400
            assert error_dict['error_message'] == 'Test error'
            assert error_dict['error_type'] == 'ValidationError'
            assert 'request_time' in error_dict


class TestErrorService:
    """Test cases for ErrorService."""
    
    def test_log_error_success(self, app):
        """Test successful error logging."""
        with app.app_context():
            error_log = ErrorService.log_error(
                method='GET',
                endpoint='/api/test',
                status_code=200,
                request_data={'test': 'data'},
                client_ip='127.0.0.1'
            )
            
            assert error_log.id is not None
            assert error_log.method == 'GET'
            assert error_log.endpoint == '/api/test'
            assert error_log.status_code == 200
            assert error_log.request_data == {'test': 'data'}
            assert error_log.client_ip == '127.0.0.1'
    
    def test_log_error_validation_failure(self, app):
        """Test error logging with missing required fields."""
        with app.app_context():
            with pytest.raises(ValueError):
                ErrorService.log_error(
                    method='',
                    endpoint='',
                    status_code=0
                )
    
    def test_log_error_headers_sanitization(self, app):
        """Test that sensitive headers are sanitized."""
        with app.app_context():
            headers = {
                'Authorization': 'Bearer token123',
                'Cookie': 'session=abc123',
                'Content-Type': 'application/json',
                'User-Agent': 'test-agent'
            }
            
            error_log = ErrorService.log_error(
                method='POST',
                endpoint='/api/test',
                status_code=200,
                request_headers=headers
            )
            
            # Sensitive headers should be removed
            assert 'Authorization' not in error_log.request_headers
            assert 'Cookie' not in error_log.request_headers
            # Non-sensitive headers should remain
            assert 'Content-Type' in error_log.request_headers
            assert 'User-Agent' in error_log.request_headers
    
    def test_get_error_by_id(self, app):
        """Test retrieving error by ID."""
        with app.app_context():
            # Create test error
            error = Error(
                method='GET',
                endpoint='/api/test',
                status_code=200
            )
            db.session.add(error)
            db.session.commit()
            
            # Retrieve error
            retrieved_error = ErrorService.get_error_by_id(error.id)
            
            assert retrieved_error is not None
            assert retrieved_error.id == error.id
            assert retrieved_error.method == 'GET'
    
    def test_get_error_by_id_not_found(self, app):
        """Test retrieving non-existent error."""
        with app.app_context():
            error = ErrorService.get_error_by_id(99999)
            assert error is None
    
    def test_get_errors_with_filters(self, app):
        """Test getting errors with various filters."""
        with app.app_context():
            # Create test errors
            error1 = Error(method='GET', endpoint='/api/test1', status_code=200)
            error2 = Error(method='POST', endpoint='/api/test2', status_code=400)
            error3 = Error(method='GET', endpoint='/api/test3', status_code=500)
            
            db.session.add_all([error1, error2, error3])
            db.session.commit()
            
            # Test filtering by method
            result = ErrorService.get_errors(method='GET')
            assert len(result['errors']) == 2
            
            # Test filtering by status code
            result = ErrorService.get_errors(status_code=400)
            assert len(result['errors']) == 1
            assert result['errors'][0].status_code == 400
    
    def test_get_error_statistics(self, app):
        """Test getting error statistics."""
        with app.app_context():
            # Create test errors
            errors = [
                Error(method='GET', endpoint='/api/test1', status_code=200),
                Error(method='POST', endpoint='/api/test2', status_code=400),
                Error(method='GET', endpoint='/api/test1', status_code=200),
                Error(method='DELETE', endpoint='/api/test3', status_code=500)
            ]
            
            db.session.add_all(errors)
            db.session.commit()
            
            stats = ErrorService.get_error_statistics()
            
            assert stats['total_requests'] == 4
            assert stats['status_code_counts']['200'] == 2
            assert stats['status_code_counts']['400'] == 1
            assert stats['status_code_counts']['500'] == 1
            assert stats['method_counts']['GET'] == 2
            assert stats['method_counts']['POST'] == 1
            assert stats['method_counts']['DELETE'] == 1
    
    def test_delete_old_errors(self, app):
        """Test deleting old error logs."""
        with app.app_context():
            # Create old error (31 days ago)
            old_time = datetime.utcnow() - timedelta(days=31)
            old_error = Error(
                method='GET',
                endpoint='/api/old',
                status_code=200,
                request_time=old_time
            )
            
            # Create recent error (1 day ago)
            recent_time = datetime.utcnow() - timedelta(days=1)
            recent_error = Error(
                method='GET',
                endpoint='/api/recent',
                status_code=200,
                request_time=recent_time
            )
            
            db.session.add_all([old_error, recent_error])
            db.session.commit()
            
            # Delete errors older than 30 days
            deleted_count = ErrorService.delete_old_errors(days=30)
            
            assert deleted_count == 1
            
            # Check that old error is deleted
            old_error_check = Error.query.get(old_error.id)
            assert old_error_check is None
            
            # Check that recent error still exists
            recent_error_check = Error.query.get(recent_error.id)
            assert recent_error_check is not None


class TestErrorAPI:
    """Test cases for error API endpoints."""
    
    def test_get_errors_endpoint(self, client):
        """Test GET /api/errors endpoint."""
        response = client.get('/api/errors')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'errors' in data['data']
        assert 'total' in data['data']
    
    def test_get_error_by_id_endpoint(self, client, app):
        """Test GET /api/errors/<id> endpoint."""
        with app.app_context():
            # Create test error
            error = Error(
                method='GET',
                endpoint='/api/test',
                status_code=200
            )
            db.session.add(error)
            db.session.commit()
            
            response = client.get(f'/api/errors/{error.id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['method'] == 'GET'
            assert data['data']['endpoint'] == '/api/test'
    
    def test_get_error_by_id_not_found(self, client):
        """Test GET /api/errors/<id> with non-existent ID."""
        response = client.get('/api/errors/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_error_statistics_endpoint(self, client):
        """Test GET /api/errors/statistics endpoint."""
        response = client.get('/api/errors/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'total_requests' in data['data']
        assert 'status_code_counts' in data['data']
        assert 'method_counts' in data['data']
    
    def test_cleanup_old_errors_endpoint(self, client):
        """Test DELETE /api/errors/cleanup endpoint."""
        response = client.delete('/api/errors/cleanup?days=30')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'deleted_count' in data['data']
    
    def test_export_errors_endpoint(self, client):
        """Test GET /api/errors/export endpoint."""
        response = client.get('/api/errors/export')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'export_info' in data['data']
        assert 'errors' in data['data']


class TestRequestLoggingMiddleware:
    """Test cases for request logging middleware."""
    
    def test_middleware_logs_request(self, client, app):
        """Test that middleware logs API requests."""
        with app.app_context():
            # Make a request
            response = client.get('/api/health')
            
            assert response.status_code == 200
            
            # Check that request was logged
            errors = Error.query.all()
            assert len(errors) > 0
            
            # Find the health check log
            health_log = next((e for e in errors if 'health' in e.endpoint), None)
            assert health_log is not None
            assert health_log.method == 'GET'
            assert health_log.status_code == 200
    
    def test_middleware_logs_error_responses(self, client, app):
        """Test that middleware logs error responses."""
        with app.app_context():
            # Make a request to non-existent endpoint
            response = client.get('/api/nonexistent')
            
            assert response.status_code == 404
            
            # Check that error was logged
            errors = Error.query.all()
            error_log = next((e for e in errors if e.status_code == 404), None)
            assert error_log is not None
            assert error_log.status_code == 404
            assert error_log.error_type == 'HTTPError'
    
    def test_middleware_calculates_duration(self, client, app):
        """Test that middleware calculates request duration."""
        with app.app_context():
            # Make a request
            response = client.get('/api/health')
            
            assert response.status_code == 200
            
            # Check that duration was calculated
            errors = Error.query.all()
            health_log = next((e for e in errors if 'health' in e.endpoint), None)
            assert health_log is not None
            assert health_log.duration_ms is not None
            assert health_log.duration_ms >= 0 