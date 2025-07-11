"""
Pytest configuration and fixtures for Link Organizer tests.
"""

import pytest
import os
import tempfile
from app import create_app, db
from models.category import Category
from models.link import Link

@pytest.fixture
def app():
    """
    Create and configure a new app instance for each test.
    
    Returns:
        Flask app instance configured for testing
    """
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    A test client for the app.
    
    Args:
        app: Flask app instance
        
    Returns:
        Flask test client
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    A test runner for the app's Click commands.
    
    Args:
        app: Flask app instance
        
    Returns:
        Flask test runner
    """
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """
    Database session for testing.
    
    Args:
        app: Flask app instance
        
    Returns:
        SQLAlchemy database session
    """
    with app.app_context():
        yield db.session

@pytest.fixture
def sample_categories(db_session):
    """
    Create sample categories for testing.
    
    Args:
        db_session: Database session
        
    Returns:
        List of created Category objects
    """
    categories = [
        Category(name='Work', description='Work-related links'),
        Category(name='Personal', description='Personal links'),
        Category(name='Learning', description='Learning resources')
    ]
    
    for category in categories:
        db_session.add(category)
    db_session.commit()
    
    return categories

@pytest.fixture
def sample_links(db_session, sample_categories):
    """
    Create sample links for testing.
    
    Args:
        db_session: Database session
        sample_categories: List of Category objects
        
    Returns:
        List of created Link objects
    """
    work_category = sample_categories[0]
    personal_category = sample_categories[1]
    
    links = [
        Link(
            title='Google',
            url='https://google.com',
            description='Search engine',
            category_id=work_category.id,
            pinned=True
        ),
        Link(
            title='GitHub',
            url='https://github.com',
            description='Code repository',
            category_id=work_category.id,
            pinned=False
        ),
        Link(
            title='YouTube',
            url='https://youtube.com',
            description='Video platform',
            category_id=personal_category.id,
            pinned=False
        ),
        Link(
            title='Stack Overflow',
            url='https://stackoverflow.com',
            description='Developer Q&A',
            category_id=None,
            pinned=True
        )
    ]
    
    for link in links:
        db_session.add(link)
    db_session.commit()
    
    return links

@pytest.fixture
def auth_headers():
    """
    Authentication headers for testing (if needed in the future).
    
    Returns:
        Dict with authentication headers
    """
    return {
        'Content-Type': 'application/json'
    } 