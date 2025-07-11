"""
Unit tests for database models.
"""

import pytest
from datetime import datetime
from models.category import Category, CategorySchema
from models.link import Link, LinkSchema

class TestCategoryModel:
    """Test cases for Category model."""
    
    def test_category_creation(self, db_session):
        """Test creating a new category."""
        category = Category(name='Test Category', description='Test description')
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == 'Test Category'
        assert category.description == 'Test description'
        assert category.created_at is not None
        assert category.updated_at is not None
    
    def test_category_repr(self, db_session):
        """Test category string representation."""
        category = Category(name='Test Category')
        db_session.add(category)
        db_session.commit()
        
        assert str(category) == f'<Category(id={category.id}, name="Test Category")>'
    
    def test_category_to_dict(self, db_session):
        """Test category to dictionary conversion."""
        category = Category(name='Test Category', description='Test description')
        db_session.add(category)
        db_session.commit()
        
        category_dict = category.to_dict()
        
        assert category_dict['id'] == category.id
        assert category_dict['name'] == 'Test Category'
        assert category_dict['description'] == 'Test description'
        assert category_dict['links_count'] == 0
        assert 'created_at' in category_dict
        assert 'updated_at' in category_dict
    
    def test_category_find_by_name(self, db_session):
        """Test finding category by name."""
        category = Category(name='Unique Category')
        db_session.add(category)
        db_session.commit()
        
        found = Category.find_by_name('Unique Category')
        assert found is not None
        assert found.id == category.id
        
        not_found = Category.find_by_name('Non-existent')
        assert not_found is None
    
    def test_category_get_all_ordered(self, db_session):
        """Test getting all categories ordered by name."""
        categories = [
            Category(name='Zebra'),
            Category(name='Alpha'),
            Category(name='Beta')
        ]
        
        for category in categories:
            db_session.add(category)
        db_session.commit()
        
        ordered_categories = Category.get_all_ordered()
        assert len(ordered_categories) == 3
        assert ordered_categories[0].name == 'Alpha'
        assert ordered_categories[1].name == 'Beta'
        assert ordered_categories[2].name == 'Zebra'
    
    def test_category_update(self, db_session):
        """Test updating category attributes."""
        category = Category(name='Original Name')
        db_session.add(category)
        db_session.commit()
        
        original_updated_at = category.updated_at
        
        category.update(name='Updated Name', description='New description')
        db_session.commit()
        
        assert category.name == 'Updated Name'
        assert category.description == 'New description'
        assert category.updated_at > original_updated_at

class TestLinkModel:
    """Test cases for Link model."""
    
    def test_link_creation(self, db_session, sample_categories):
        """Test creating a new link."""
        category = sample_categories[0]
        link = Link(
            title='Test Link',
            url='https://example.com',
            description='Test description',
            category_id=category.id,
            pinned=True
        )
        db_session.add(link)
        db_session.commit()
        
        assert link.id is not None
        assert link.title == 'Test Link'
        assert link.url == 'https://example.com'
        assert link.description == 'Test description'
        assert link.category_id == category.id
        assert link.pinned is True
        assert link.created_at is not None
        assert link.updated_at is not None
    
    def test_link_repr(self, db_session):
        """Test link string representation."""
        link = Link(title='Test Link', url='https://example.com')
        db_session.add(link)
        db_session.commit()
        
        assert str(link) == f'<Link(id={link.id}, title="Test Link", url="https://example.com")>'
    
    def test_link_to_dict(self, db_session, sample_categories):
        """Test link to dictionary conversion."""
        category = sample_categories[0]
        link = Link(
            title='Test Link',
            url='https://example.com',
            description='Test description',
            category_id=category.id,
            pinned=True
        )
        db_session.add(link)
        db_session.commit()
        
        link_dict = link.to_dict()
        
        assert link_dict['id'] == link.id
        assert link_dict['title'] == 'Test Link'
        assert link_dict['url'] == 'https://example.com'
        assert link_dict['description'] == 'Test description'
        assert link_dict['categoryId'] == category.id
        assert link_dict['categoryName'] == category.name
        assert link_dict['pinned'] is True
        assert 'createdAt' in link_dict
        assert 'updatedAt' in link_dict
    
    def test_link_find_by_url(self, db_session):
        """Test finding link by URL."""
        link = Link(title='Test Link', url='https://unique.com')
        db_session.add(link)
        db_session.commit()
        
        found = Link.find_by_url('https://unique.com')
        assert found is not None
        assert found.id == link.id
        
        not_found = Link.find_by_url('https://non-existent.com')
        assert not_found is None
    
    def test_link_get_by_category(self, db_session, sample_categories):
        """Test getting links by category."""
        category = sample_categories[0]
        
        links = [
            Link(title='Link 1', url='https://example1.com', category_id=category.id, pinned=True),
            Link(title='Link 2', url='https://example2.com', category_id=category.id, pinned=False),
            Link(title='Link 3', url='https://example3.com', category_id=None, pinned=False)
        ]
        
        for link in links:
            db_session.add(link)
        db_session.commit()
        
        category_links = Link.get_by_category(category.id)
        assert len(category_links) == 2
        assert category_links[0].pinned is True  # Pinned links first
        assert category_links[1].pinned is False
    
    def test_link_get_pinned_links(self, db_session):
        """Test getting pinned links."""
        links = [
            Link(title='Pinned 1', url='https://pinned1.com', pinned=True),
            Link(title='Pinned 2', url='https://pinned2.com', pinned=True),
            Link(title='Unpinned', url='https://unpinned.com', pinned=False)
        ]
        
        for link in links:
            db_session.add(link)
        db_session.commit()
        
        pinned_links = Link.get_pinned_links()
        assert len(pinned_links) == 2
        assert all(link.pinned for link in pinned_links)
    
    def test_link_search_by_title(self, db_session):
        """Test searching links by title."""
        links = [
            Link(title='Python Tutorial', url='https://python.com'),
            Link(title='JavaScript Guide', url='https://js.com'),
            Link(title='Python Best Practices', url='https://python-best.com')
        ]
        
        for link in links:
            db_session.add(link)
        db_session.commit()
        
        python_links = Link.search_by_title('Python')
        assert len(python_links) == 2
        
        js_links = Link.search_by_title('JavaScript')
        assert len(js_links) == 1
        
        no_results = Link.search_by_title('Non-existent')
        assert len(no_results) == 0
    
    def test_link_update(self, db_session, sample_categories):
        """Test updating link attributes."""
        category = sample_categories[0]
        link = Link(title='Original Title', url='https://original.com')
        db_session.add(link)
        db_session.commit()
        
        original_updated_at = link.updated_at
        
        link.update(
            title='Updated Title',
            url='https://updated.com',
            description='New description',
            category_id=category.id,
            pinned=True
        )
        db_session.commit()
        
        assert link.title == 'Updated Title'
        assert link.url == 'https://updated.com'
        assert link.description == 'New description'
        assert link.category_id == category.id
        assert link.pinned is True
        assert link.updated_at > original_updated_at
    
    def test_link_toggle_pin(self, db_session):
        """Test toggling link pin status."""
        link = Link(title='Test Link', url='https://example.com', pinned=False)
        db_session.add(link)
        db_session.commit()
        
        original_updated_at = link.updated_at
        
        # Toggle to pinned
        link.toggle_pin()
        db_session.commit()
        assert link.pinned is True
        assert link.updated_at > original_updated_at
        
        # Toggle to unpinned
        link.toggle_pin()
        db_session.commit()
        assert link.pinned is False
    
    def test_link_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert Link.validate_url('https://example.com') is True
        assert Link.validate_url('http://example.com') is True
        assert Link.validate_url('https://sub.example.com/path?param=value') is True
        
        # Invalid URLs
        assert Link.validate_url('example.com') is False
        assert Link.validate_url('ftp://example.com') is False
        assert Link.validate_url('not-a-url') is False
        assert Link.validate_url('') is False

class TestSchemas:
    """Test cases for Marshmallow schemas."""
    
    def test_category_schema_validation(self):
        """Test CategorySchema validation."""
        schema = CategorySchema()
        
        # Valid data
        valid_data = {'name': 'Test Category', 'description': 'Test description'}
        errors = schema.validate(valid_data)
        assert not errors
        
        # Invalid data - missing name
        invalid_data = {'description': 'Test description'}
        errors = schema.validate(invalid_data)
        assert 'name' in errors
        
        # Invalid data - name too long
        invalid_data = {'name': 'a' * 101, 'description': 'Test description'}
        errors = schema.validate(invalid_data)
        assert 'name' in errors
    
    def test_link_schema_validation(self):
        """Test LinkSchema validation."""
        schema = LinkSchema()
        
        # Valid data
        valid_data = {
            'title': 'Test Link',
            'url': 'https://example.com',
            'description': 'Test description',
            'categoryId': 1,
            'pinned': True
        }
        errors = schema.validate(valid_data)
        assert not errors
        
        # Invalid data - missing title
        invalid_data = {'url': 'https://example.com'}
        errors = schema.validate(invalid_data)
        assert 'title' in errors
        
        # Invalid data - missing URL
        invalid_data = {'title': 'Test Link'}
        errors = schema.validate(invalid_data)
        assert 'url' in errors
        
        # Invalid data - title too long
        invalid_data = {
            'title': 'a' * 201,
            'url': 'https://example.com'
        }
        errors = schema.validate(invalid_data)
        assert 'title' in errors 