"""
Category service layer for business logic and data operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from models.category import Category, category_schema, categories_schema, category_create_schema, category_update_schema
from extensions import db

class CategoryService:
    """
    Service class for category-related operations.
    
    Provides business logic for creating, reading, updating, and deleting categories.
    Handles data validation, error handling, and database operations.
    """
    
    @staticmethod
    def get_all_categories() -> List[Dict[str, Any]]:
        """
        Retrieve all categories ordered by name.
        
        Returns:
            List[Dict]: List of category dictionaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            categories = Category.get_all_ordered()
            return categories_schema.dump(categories)
        except Exception as e:
            raise Exception(f"Failed to retrieve categories: {str(e)}")
    
    @staticmethod
    def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a category by its ID.
        
        Args:
            category_id (int): The ID of the category to retrieve
            
        Returns:
            Optional[Dict]: Category dictionary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            category = Category.query.get(category_id)
            if not category:
                return None
            return category_schema.dump(category)
        except Exception as e:
            raise Exception(f"Failed to retrieve category: {str(e)}")
    
    @staticmethod
    def create_category(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new category.
        
        Args:
            data (Dict): Category data containing 'name' and optional 'description'
            
        Returns:
            Dict: Created category data
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Validate input data
            errors = category_create_schema.validate(data)
            if errors:
                raise ValueError(f"Validation errors: {errors}")
            
            # Check if category already exists
            existing_category = Category.find_by_name(data['name'])
            if existing_category:
                raise ValueError(f"Category '{data['name']}' already exists")
            
            # Create new category
            category = Category(
                name=data['name'],
                description=data.get('description')
            )
            
            db.session.add(category)
            db.session.commit()
            
            return category_schema.dump(category)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Category '{data.get('name', '')}' already exists")
        except ValueError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create category: {str(e)}")
    
    @staticmethod
    def update_category(category_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing category.
        
        Args:
            category_id (int): The ID of the category to update
            data (Dict): Updated category data
            
        Returns:
            Optional[Dict]: Updated category data if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Validate input data
            errors = category_update_schema.validate(data)
            if errors:
                raise ValueError(f"Validation errors: {errors}")
            
            # Find category
            category = Category.query.get(category_id)
            if not category:
                return None
            
            # Check if new name conflicts with existing category
            if 'name' in data and data['name'] != category.name:
                existing_category = Category.find_by_name(data['name'])
                if existing_category:
                    raise ValueError(f"Category '{data['name']}' already exists")
            
            # Update category
            category.update(**data)
            db.session.commit()
            
            return category_schema.dump(category)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Category '{data.get('name', '')}' already exists")
        except ValueError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update category: {str(e)}")
    
    @staticmethod
    def delete_category(category_id: int) -> bool:
        """
        Delete a category and set its links to uncategorized.
        
        Args:
            category_id (int): The ID of the category to delete
            
        Returns:
            bool: True if category was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            category = Category.query.get(category_id)
            if not category:
                return False
            
            # Set category_id to NULL for all links in this category
            from models.link import Link
            Link.query.filter_by(category_id=category_id).update({'category_id': None})
            
            # Delete the category
            db.session.delete(category)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete category: {str(e)}")
    
    @staticmethod
    def get_category_stats() -> Dict[str, Any]:
        """
        Get statistics about categories.
        
        Returns:
            Dict: Statistics including total categories and links per category
            
        Raises:
            Exception: If database operation fails
        """
        try:
            from models.link import Link
            
            # Get total categories
            total_categories = Category.query.count()
            
            # Get links count per category
            categories_with_links = db.session.query(
                Category.id,
                Category.name,
                db.func.count(Link.id).label('links_count')
            ).outerjoin(Link).group_by(Category.id, Category.name).all()
            
            stats = {
                'total_categories': total_categories,
                'categories_with_links': [
                    {
                        'id': cat.id,
                        'name': cat.name,
                        'links_count': cat.links_count
                    }
                    for cat in categories_with_links
                ]
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Failed to get category statistics: {str(e)}") 