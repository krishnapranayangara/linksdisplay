"""
Link API endpoints for CRUD operations.
"""

from flask import Blueprint, request, jsonify
from services.link_service import LinkService
from marshmallow import ValidationError

links_bp = Blueprint('links', __name__, url_prefix='/api/links')

@links_bp.route('', methods=['GET'])
@links_bp.route('/', methods=['GET'])
def get_links():
    """
    Get all links, optionally filtered by category.
    
    Query Parameters:
        category_id (int, optional): Filter links by category ID
        
    Returns:
        JSON response with list of links
        
    ---
    tags:
      - Links
    parameters:
      - name: category_id
        in: query
        type: integer
        required: false
        description: Filter links by category ID
    responses:
      200:
        description: List of links retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Link ID
              title:
                type: string
                description: Link title
              url:
                type: string
                description: Link URL
              description:
                type: string
                description: Link description
              categoryId:
                type: integer
                description: Category ID
              categoryName:
                type: string
                description: Category name
              pinned:
                type: boolean
                description: Whether link is pinned
              createdAt:
                type: string
                format: date-time
                description: Creation timestamp
              updatedAt:
                type: string
                format: date-time
                description: Last update timestamp
      500:
        description: Internal server error
    """
    try:
        category_id = request.args.get('category_id', type=int)
        links = LinkService.get_all_links(category_id)
        return jsonify({
            'success': True,
            'data': links,
            'count': len(links)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/<int:link_id>', methods=['GET'])
def get_link(link_id):
    """
    Get a specific link by ID.
    
    Args:
        link_id (int): The ID of the link to retrieve
        
    Returns:
        JSON response with link data
        
    ---
    tags:
      - Links
    parameters:
      - name: link_id
        in: path
        required: true
        type: integer
        description: Link ID
    responses:
      200:
        description: Link retrieved successfully
      404:
        description: Link not found
      500:
        description: Internal server error
    """
    try:
        link = LinkService.get_link_by_id(link_id)
        if not link:
            return jsonify({
                'success': False,
                'error': 'Link not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': link
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('', methods=['POST'])
@links_bp.route('/', methods=['POST'])
def create_link():
    """
    Create a new link.
    
    Request Body:
        JSON object with link data
        
    Returns:
        JSON response with created link data
        
    ---
    tags:
      - Links
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - url
          properties:
            title:
              type: string
              description: Link title (1-200 characters)
            url:
              type: string
              description: Link URL (must include http/https)
            description:
              type: string
              description: Optional link description
            categoryId:
              type: integer
              description: Category ID (optional)
            pinned:
              type: boolean
              description: Whether link is pinned
    responses:
      201:
        description: Link created successfully
      400:
        description: Bad request - validation error
      409:
        description: Conflict - link already exists
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        link = LinkService.create_link(data)
        return jsonify({
            'success': True,
            'data': link,
            'message': 'Link created successfully'
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/<int:link_id>', methods=['PUT'])
def update_link(link_id):
    """
    Update an existing link.
    
    Args:
        link_id (int): The ID of the link to update
        
    Request Body:
        JSON object with updated link data
        
    Returns:
        JSON response with updated link data
        
    ---
    tags:
      - Links
    parameters:
      - name: link_id
        in: path
        required: true
        type: integer
        description: Link ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: Link title
            url:
              type: string
              description: Link URL
            description:
              type: string
              description: Link description
            categoryId:
              type: integer
              description: Category ID
            pinned:
              type: boolean
              description: Whether link is pinned
    responses:
      200:
        description: Link updated successfully
      400:
        description: Bad request - validation error
      404:
        description: Link not found
      409:
        description: Conflict - link URL already exists
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        link = LinkService.update_link(link_id, data)
        if not link:
            return jsonify({
                'success': False,
                'error': 'Link not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': link,
            'message': 'Link updated successfully'
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    """
    Delete a link.
    
    Args:
        link_id (int): The ID of the link to delete
        
    Returns:
        JSON response with deletion status
        
    ---
    tags:
      - Links
    parameters:
      - name: link_id
        in: path
        required: true
        type: integer
        description: Link ID
    responses:
      200:
        description: Link deleted successfully
      404:
        description: Link not found
      500:
        description: Internal server error
    """
    try:
        deleted = LinkService.delete_link(link_id)
        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Link not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Link deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/<int:link_id>/pin', methods=['PATCH'])
def toggle_pin_link(link_id):
    """
    Toggle the pinned status of a link.
    
    Args:
        link_id (int): The ID of the link to toggle pin status
        
    Request Body:
        JSON object with pinned status
        
    Returns:
        JSON response with updated link data
        
    ---
    tags:
      - Links
    parameters:
      - name: link_id
        in: path
        required: true
        type: integer
        description: Link ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            pinned:
              type: boolean
              description: New pinned status
    responses:
      200:
        description: Link pin status updated successfully
      404:
        description: Link not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        link = LinkService.toggle_pin_link(link_id)
        if not link:
            return jsonify({
                'success': False,
                'error': 'Link not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': link,
            'message': 'Link pin status updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/search', methods=['GET'])
def search_links():
    """
    Search links by title (case-insensitive).
    
    Query Parameters:
        q (str): Search term (minimum 2 characters)
        
    Returns:
        JSON response with matching links
        
    ---
    tags:
      - Links
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search term (minimum 2 characters)
    responses:
      200:
        description: Search results retrieved successfully
      400:
        description: Bad request - search term too short
      500:
        description: Internal server error
    """
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Search term is required'
            }), 400
        
        links = LinkService.search_links(search_term)
        return jsonify({
            'success': True,
            'data': links,
            'count': len(links),
            'search_term': search_term
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/pinned', methods=['GET'])
def get_pinned_links():
    """
    Get all pinned links.
    
    Returns:
        JSON response with pinned links
        
    ---
    tags:
      - Links
    responses:
      200:
        description: Pinned links retrieved successfully
      500:
        description: Internal server error
    """
    try:
        links = LinkService.get_pinned_links()
        return jsonify({
            'success': True,
            'data': links,
            'count': len(links)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@links_bp.route('/stats', methods=['GET'])
def get_link_stats():
    """
    Get statistics about links.
    
    Returns:
        JSON response with link statistics
        
    ---
    tags:
      - Links
    responses:
      200:
        description: Link statistics retrieved successfully
      500:
        description: Internal server error
    """
    try:
        stats = LinkService.get_link_stats()
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 