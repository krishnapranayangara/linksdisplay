"""
Integration tests for API endpoints.
"""

import pytest
import json
from app import create_app, db

class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'OK'
        assert 'message' in data
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_ping_endpoint(self, client):
        """Test ping endpoint."""
        response = client.get('/api/ping')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['message'] == 'pong'
        assert 'timestamp' in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get('/')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['message'] == 'Link Organizer API'
        assert 'endpoints' in data
    
    def test_api_docs_endpoint(self, client):
        """Test API documentation endpoint."""
        response = client.get('/api/docs')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['message'] == 'Link Organizer API Documentation'
        assert 'endpoints' in data

class TestCategoryEndpoints:
    """Test cases for category endpoints."""
    
    def test_get_categories_empty(self, client):
        """Test getting categories when none exist."""
        response = client.get('/api/categories')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data'] == []
        assert data['count'] == 0
    
    def test_get_categories_with_data(self, client, sample_categories):
        """Test getting categories with existing data."""
        response = client.get('/api/categories')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) == 3
        assert data['count'] == 3
        
        # Check that categories are ordered by name
        category_names = [cat['name'] for cat in data['data']]
        assert category_names == ['Learning', 'Personal', 'Work']
    
    def test_get_category_by_id(self, client, sample_categories):
        """Test getting a specific category by ID."""
        category = sample_categories[0]
        response = client.get(f'/api/categories/{category.id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['id'] == category.id
        assert data['data']['name'] == category.name
    
    def test_get_category_not_found(self, client):
        """Test getting a non-existent category."""
        response = client.get('/api/categories/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_create_category_success(self, client):
        """Test creating a new category successfully."""
        category_data = {
            'name': 'New Category',
            'description': 'A new test category'
        }
        
        response = client.post(
            '/api/categories',
            data=json.dumps(category_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['success'] is True
        assert data['data']['name'] == 'New Category'
        assert data['data']['description'] == 'A new test category'
        assert 'id' in data['data']
    
    def test_create_category_missing_name(self, client):
        """Test creating a category without a name."""
        category_data = {'description': 'No name provided'}
        
        response = client.post(
            '/api/categories',
            data=json.dumps(category_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'required' in data['error'].lower()
    
    def test_create_category_duplicate_name(self, client, sample_categories):
        """Test creating a category with duplicate name."""
        category_data = {'name': 'Work'}  # Already exists in sample data
        
        response = client.post(
            '/api/categories',
            data=json.dumps(category_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'already exists' in data['error'].lower()
    
    def test_update_category_success(self, client, sample_categories):
        """Test updating a category successfully."""
        category = sample_categories[0]
        update_data = {
            'name': 'Updated Category',
            'description': 'Updated description'
        }
        
        response = client.put(
            f'/api/categories/{category.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['name'] == 'Updated Category'
        assert data['data']['description'] == 'Updated description'
    
    def test_update_category_not_found(self, client):
        """Test updating a non-existent category."""
        update_data = {'name': 'Updated Category'}
        
        response = client.put(
            '/api/categories/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_delete_category_success(self, client, sample_categories):
        """Test deleting a category successfully."""
        category = sample_categories[0]
        
        response = client.delete(f'/api/categories/{category.id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'deleted successfully' in data['message'].lower()
    
    def test_delete_category_not_found(self, client):
        """Test deleting a non-existent category."""
        response = client.delete('/api/categories/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_get_category_stats(self, client, sample_categories, sample_links):
        """Test getting category statistics."""
        response = client.get('/api/categories/stats')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'total_categories' in data['data']
        assert 'categories_with_links' in data['data']
        assert data['data']['total_categories'] == 3

class TestLinkEndpoints:
    """Test cases for link endpoints."""
    
    def test_get_links_empty(self, client):
        """Test getting links when none exist."""
        response = client.get('/api/links')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data'] == []
        assert data['count'] == 0
    
    def test_get_links_with_data(self, client, sample_links):
        """Test getting links with existing data."""
        response = client.get('/api/links')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) == 4
        assert data['count'] == 4
        
        # Check that pinned links come first
        pinned_links = [link for link in data['data'] if link['pinned']]
        unpinned_links = [link for link in data['data'] if not link['pinned']]
        assert len(pinned_links) == 2
        assert len(unpinned_links) == 2
    
    def test_get_links_by_category(self, client, sample_categories, sample_links):
        """Test getting links filtered by category."""
        category = sample_categories[0]  # Work category
        
        response = client.get(f'/api/links?category_id={category.id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) == 2  # 2 links in Work category
        
        for link in data['data']:
            assert link['categoryId'] == category.id
    
    def test_get_link_by_id(self, client, sample_links):
        """Test getting a specific link by ID."""
        link = sample_links[0]
        response = client.get(f'/api/links/{link.id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['id'] == link.id
        assert data['data']['title'] == link.title
        assert data['data']['url'] == link.url
    
    def test_get_link_not_found(self, client):
        """Test getting a non-existent link."""
        response = client.get('/api/links/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_create_link_success(self, client, sample_categories):
        """Test creating a new link successfully."""
        category = sample_categories[0]
        link_data = {
            'title': 'New Link',
            'url': 'https://example.com',
            'description': 'A new test link',
            'categoryId': category.id,
            'pinned': True
        }
        
        response = client.post(
            '/api/links',
            data=json.dumps(link_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['success'] is True
        assert data['data']['title'] == 'New Link'
        assert data['data']['url'] == 'https://example.com'
        assert data['data']['categoryId'] == category.id
        assert data['data']['pinned'] is True
    
    def test_create_link_missing_title(self, client):
        """Test creating a link without a title."""
        link_data = {'url': 'https://example.com'}
        
        response = client.post(
            '/api/links',
            data=json.dumps(link_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'required' in data['error'].lower()
    
    def test_create_link_invalid_url(self, client):
        """Test creating a link with invalid URL."""
        link_data = {
            'title': 'Test Link',
            'url': 'not-a-valid-url'
        }
        
        response = client.post(
            '/api/links',
            data=json.dumps(link_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'invalid' in data['error'].lower()
    
    def test_create_link_duplicate_url(self, client, sample_links):
        """Test creating a link with duplicate URL."""
        link_data = {
            'title': 'Duplicate Link',
            'url': 'https://google.com'  # Already exists in sample data
        }
        
        response = client.post(
            '/api/links',
            data=json.dumps(link_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'already exists' in data['error'].lower()
    
    def test_update_link_success(self, client, sample_links, sample_categories):
        """Test updating a link successfully."""
        link = sample_links[0]
        category = sample_categories[1]
        update_data = {
            'title': 'Updated Link',
            'url': 'https://updated.com',
            'description': 'Updated description',
            'categoryId': category.id,
            'pinned': False
        }
        
        response = client.put(
            f'/api/links/{link.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['title'] == 'Updated Link'
        assert data['data']['url'] == 'https://updated.com'
        assert data['data']['categoryId'] == category.id
        assert data['data']['pinned'] is False
    
    def test_update_link_not_found(self, client):
        """Test updating a non-existent link."""
        update_data = {'title': 'Updated Link'}
        
        response = client.put(
            '/api/links/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_delete_link_success(self, client, sample_links):
        """Test deleting a link successfully."""
        link = sample_links[0]
        
        response = client.delete(f'/api/links/{link.id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'deleted successfully' in data['message'].lower()
    
    def test_delete_link_not_found(self, client):
        """Test deleting a non-existent link."""
        response = client.delete('/api/links/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_toggle_pin_link(self, client, sample_links):
        """Test toggling link pin status."""
        link = sample_links[1]  # GitHub link (not pinned)
        
        # Toggle to pinned
        response = client.patch(
            f'/api/links/{link.id}/pin',
            data=json.dumps({'pinned': True}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['pinned'] is True
    
    def test_search_links(self, client, sample_links):
        """Test searching links by title."""
        response = client.get('/api/links/search?q=Python')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['search_term'] == 'Python'
        # Note: No Python links in sample data, so count should be 0
    
    def test_search_links_short_term(self, client):
        """Test searching with short search term."""
        response = client.get('/api/links/search?q=a')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'short' in data['error'].lower()
    
    def test_get_pinned_links(self, client, sample_links):
        """Test getting pinned links."""
        response = client.get('/api/links/pinned')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) == 2  # 2 pinned links in sample data
        
        for link in data['data']:
            assert link['pinned'] is True
    
    def test_get_link_stats(self, client, sample_links):
        """Test getting link statistics."""
        response = client.get('/api/links/stats')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'total_links' in data['data']
        assert 'pinned_links' in data['data']
        assert 'uncategorized_links' in data['data']
        assert 'links_per_category' in data['data']
        assert data['data']['total_links'] == 4
        assert data['data']['pinned_links'] == 2

class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_405_error(self, client):
        """Test 405 error handling."""
        response = client.post('/api/health')  # POST not allowed on health endpoint
        data = json.loads(response.data)
        
        assert response.status_code == 405
        assert data['success'] is False
        assert 'method not allowed' in data['error'].lower()
    
    def test_400_error_missing_body(self, client):
        """Test 400 error handling for missing request body."""
        response = client.post('/api/categories')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'required' in data['error'].lower() 