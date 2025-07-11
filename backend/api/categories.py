"""
Category API endpoints for CRUD operations.
"""

from flask import Blueprint, request, jsonify
from services.category_service import CategoryService
from marshmallow import ValidationError

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@categories_bp.route('', methods=['GET'])
@categories_bp.route('/', methods=['GET'])
def get_categories():
    """
    Get all categories.
    
    Returns:
        JSON response with list of categories
        
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Category ID
              name:
                type: string
                description: Category name
              description:
                type: string
                description: Category description
              created_at:
                type: string
                format: date-time
                description: Creation timestamp
              updated_at:
                type: string
                format: date-time
                description: Last update timestamp
              links_count:
                type: integer
                description: Number of links in this category
      500:
        description: Internal server error
    """
    try:
        categories = CategoryService.get_all_categories()
        return jsonify({
            'success': True,
            'data': categories,
            'count': len(categories)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get a specific category by ID.
    
    Args:
        category_id (int): The ID of the category to retrieve
        
    Returns:
        JSON response with category data
        
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        required: true
        type: integer
        description: Category ID
    responses:
      200:
        description: Category retrieved successfully
      404:
        description: Category not found
      500:
        description: Internal server error
    """
    try:
        category = CategoryService.get_category_by_id(category_id)
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': category
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@categories_bp.route('', methods=['POST'])
@categories_bp.route('/', methods=['POST'])
def create_category():
    """
    Create a new category.
    
    Request Body:
        JSON object with category data
        
    Returns:
        JSON response with created category data
        
    ---
    tags:
      - Categories
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Category name (1-100 characters)
            description:
              type: string
              description: Optional category description
    responses:
      201:
        description: Category created successfully
      400:
        description: Bad request - validation error
      409:
        description: Conflict - category already exists
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
        
        category = CategoryService.create_category(data)
        return jsonify({
            'success': True,
            'data': category,
            'message': 'Category created successfully'
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

@categories_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """
    Update an existing category.
    
    Args:
        category_id (int): The ID of the category to update
        
    Request Body:
        JSON object with updated category data
        
    Returns:
        JSON response with updated category data
        
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        required: true
        type: integer
        description: Category ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Category name (1-100 characters)
            description:
              type: string
              description: Category description
    responses:
      200:
        description: Category updated successfully
      400:
        description: Bad request - validation error
      404:
        description: Category not found
      409:
        description: Conflict - category name already exists
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
        
        category = CategoryService.update_category(category_id, data)
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': category,
            'message': 'Category updated successfully'
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

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """
    Delete a category and set its links to uncategorized.
    
    Args:
        category_id (int): The ID of the category to delete
        
    Returns:
        JSON response with deletion status
        
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        required: true
        type: integer
        description: Category ID
    responses:
      200:
        description: Category deleted successfully
      404:
        description: Category not found
      500:
        description: Internal server error
    """
    try:
        deleted = CategoryService.delete_category(category_id)
        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Category deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@categories_bp.route('/stats', methods=['GET'])
def get_category_stats():
    """
    Get statistics about categories.
    
    Returns:
        JSON response with category statistics
        
    ---
    tags:
      - Categories
    responses:
      200:
        description: Category statistics retrieved successfully
      500:
        description: Internal server error
    """
    try:
        stats = CategoryService.get_category_stats()
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 