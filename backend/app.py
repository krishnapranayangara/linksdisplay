"""
Main Flask application for Link Organizer API.

This module contains the Flask application factory and configuration setup.
It follows the factory pattern for better testing and modularity.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
import logging
from logging.handlers import RotatingFileHandler
import os
from extensions import db, ma

def create_app(config_name=None):
    """
    Application factory function.
    
    Creates and configures the Flask application with all necessary extensions,
    blueprints, and error handlers.
    
    Args:
        config_name (str, optional): Configuration name to use.
                                   If None, uses environment-based config.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    if config_name:
        app.config.from_object(get_config())
    else:
        app.config.from_object(get_config())
    
    # Initialize extensions
    from extensions import db, ma
    db.init_app(app)
    ma.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/link_organizer.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Link Organizer startup')
    
    # Initialize request logging middleware
    from middleware.request_logger import init_request_logger
    init_request_logger(app)
    
    # Register blueprints
    from api import categories_bp, links_bp, health_bp
    from routes.errors import errors_bp
    app.register_blueprint(categories_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(errors_bp)
    
    # Import models to ensure they are registered with SQLAlchemy
    from models import Category, Link, Error
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'message': 'The request could not be processed due to invalid data.'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'success': False,
            'error': 'Not found',
            'message': 'The requested resource was not found.'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'message': 'The HTTP method is not allowed for this endpoint.'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unhandled exceptions."""
        app.logger.error(f'Unhandled exception: {error}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint with API information."""
        return jsonify({
            'success': True,
            'message': 'Link Organizer API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'categories': '/api/categories',
                'links': '/api/links',
                'errors': '/api/errors',
                'documentation': '/api/docs'
            }
        })
    
    # API documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        """API documentation endpoint."""
        return jsonify({
            'success': True,
            'message': 'Link Organizer API Documentation',
            'version': '1.0.0',
            'endpoints': {
                'health': {
                    'GET /api/health': 'Get API health status',
                    'GET /api/ping': 'Simple ping endpoint'
                },
                'categories': {
                    'GET /api/categories': 'Get all categories',
                    'GET /api/categories/<id>': 'Get category by ID',
                    'POST /api/categories': 'Create new category',
                    'PUT /api/categories/<id>': 'Update category',
                    'DELETE /api/categories/<id>': 'Delete category',
                    'GET /api/categories/stats': 'Get category statistics'
                },
                'links': {
                    'GET /api/links': 'Get all links',
                    'GET /api/links?category_id=<id>': 'Get links by category',
                    'GET /api/links/<id>': 'Get link by ID',
                    'POST /api/links': 'Create new link',
                    'PUT /api/links/<id>': 'Update link',
                    'DELETE /api/links/<id>': 'Delete link',
                    'PATCH /api/links/<id>/pin': 'Toggle link pin status',
                    'GET /api/links/search?q=<term>': 'Search links by title',
                    'GET /api/links/pinned': 'Get pinned links',
                    'GET /api/links/stats': 'Get link statistics'
                },
                'errors': {
                    'GET /api/errors': 'Get error logs with filtering',
                    'GET /api/errors/<id>': 'Get specific error log',
                    'GET /api/errors/statistics': 'Get error statistics',
                    'DELETE /api/errors/cleanup': 'Clean up old error logs',
                    'GET /api/errors/export': 'Export error logs'
                }
            }
        })
    
    return app

def init_db():
    """Initialize the database with tables and default data."""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add default categories if they don't exist
        from models.category import Category
        default_categories = ['Work', 'Personal']
        for category_name in default_categories:
            existing = Category.query.filter_by(name=category_name).first()
            if not existing:
                category = Category(name=category_name)
                db.session.add(category)
                print(f"✅ Added default category: {category_name}")
        
        db.session.commit()
        print("✅ Database initialized successfully!")

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=3001,
        debug=app.config.get('DEBUG', False)
    ) 