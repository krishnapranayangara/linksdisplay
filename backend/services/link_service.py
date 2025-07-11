"""
Link service layer for business logic and data operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from models.link import Link, link_schema, links_schema, link_create_schema, link_update_schema
from models.category import Category
from extensions import db

class LinkService:
    """
    Service class for link-related operations.
    
    Provides business logic for creating, reading, updating, and deleting links.
    Handles data validation, error handling, and database operations.
    """
    
    @staticmethod
    def get_all_links(category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all links, optionally filtered by category.
        
        Args:
            category_id (Optional[int]): Filter links by category ID
            
        Returns:
            List[Dict]: List of link dictionaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            if category_id:
                links = Link.get_by_category(category_id)
            else:
                links = Link.query.order_by(Link.pinned.desc(), Link.created_at.desc()).all()
            
            return links_schema.dump(links)
        except Exception as e:
            raise Exception(f"Failed to retrieve links: {str(e)}")
    
    @staticmethod
    def get_link_by_id(link_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a link by its ID.
        
        Args:
            link_id (int): The ID of the link to retrieve
            
        Returns:
            Optional[Dict]: Link dictionary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            link = Link.query.get(link_id)
            if not link:
                return None
            return link_schema.dump(link)
        except Exception as e:
            raise Exception(f"Failed to retrieve link: {str(e)}")
    
    @staticmethod
    def create_link(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new link.
        
        Args:
            data (Dict): Link data containing 'title', 'url', and optional fields
            
        Returns:
            Dict: Created link data
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Validate input data
            errors = link_create_schema.validate(data)
            if errors:
                raise ValueError(f"Validation errors: {errors}")
            
            # Validate URL format
            if not Link.validate_url(data['url']):
                raise ValueError("Invalid URL format. Must include scheme (http/https) and domain.")
            
            # Check if category exists (if provided)
            if data.get('categoryId'):
                category = Category.query.get(data['categoryId'])
                if not category:
                    raise ValueError(f"Category with ID {data['categoryId']} does not exist")
            
            # Check if link already exists
            existing_link = Link.find_by_url(data['url'])
            if existing_link:
                raise ValueError(f"Link with URL '{data['url']}' already exists")
            
            # Create new link
            link = Link(
                title=data['title'],
                url=data['url'],
                description=data.get('description'),
                category_id=data.get('categoryId'),
                pinned=data.get('pinned', False)
            )
            
            db.session.add(link)
            db.session.commit()
            
            return link_schema.dump(link)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Link with URL '{data.get('url', '')}' already exists")
        except ValueError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create link: {str(e)}")
    
    @staticmethod
    def update_link(link_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing link.
        
        Args:
            link_id (int): The ID of the link to update
            data (Dict): Updated link data
            
        Returns:
            Optional[Dict]: Updated link data if found, None otherwise
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            # Validate input data
            errors = link_update_schema.validate(data)
            if errors:
                raise ValueError(f"Validation errors: {errors}")
            
            # Find link
            link = Link.query.get(link_id)
            if not link:
                return None
            
            # Validate URL format if provided
            if 'url' in data and not Link.validate_url(data['url']):
                raise ValueError("Invalid URL format. Must include scheme (http/https) and domain.")
            
            # Check if category exists (if provided)
            if data.get('categoryId'):
                category = Category.query.get(data['categoryId'])
                if not category:
                    raise ValueError(f"Category with ID {data['categoryId']} does not exist")
            
            # Check if new URL conflicts with existing link
            if 'url' in data and data['url'] != link.url:
                existing_link = Link.find_by_url(data['url'])
                if existing_link:
                    raise ValueError(f"Link with URL '{data['url']}' already exists")
            
            # Map categoryId to category_id for the model
            update_data = data.copy()
            if 'categoryId' in update_data:
                update_data['category_id'] = update_data.pop('categoryId')
            
            # Update link
            link.update(**update_data)
            db.session.commit()
            
            return link_schema.dump(link)
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Link with URL '{data.get('url', '')}' already exists")
        except ValueError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update link: {str(e)}")
    
    @staticmethod
    def delete_link(link_id: int) -> bool:
        """
        Delete a link.
        
        Args:
            link_id (int): The ID of the link to delete
            
        Returns:
            bool: True if link was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            link = Link.query.get(link_id)
            if not link:
                return False
            
            db.session.delete(link)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete link: {str(e)}")
    
    @staticmethod
    def toggle_pin_link(link_id: int) -> Optional[Dict[str, Any]]:
        """
        Toggle the pinned status of a link.
        
        Args:
            link_id (int): The ID of the link to toggle pin status
            
        Returns:
            Optional[Dict]: Updated link data if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            link = Link.query.get(link_id)
            if not link:
                return None
            
            link.toggle_pin()
            db.session.commit()
            
            return link_schema.dump(link)
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to toggle pin status: {str(e)}")
    
    @staticmethod
    def search_links(search_term: str) -> List[Dict[str, Any]]:
        """
        Search links by title (case-insensitive).
        
        Args:
            search_term (str): Search term to match against link titles
            
        Returns:
            List[Dict]: List of matching link dictionaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            if not search_term or len(search_term.strip()) < 2:
                raise ValueError("Search term must be at least 2 characters long")
            
            links = Link.search_by_title(search_term.strip())
            return links_schema.dump(links)
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Failed to search links: {str(e)}")
    
    @staticmethod
    def get_pinned_links() -> List[Dict[str, Any]]:
        """
        Get all pinned links.
        
        Returns:
            List[Dict]: List of pinned link dictionaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            links = Link.get_pinned_links()
            return links_schema.dump(links)
        except Exception as e:
            raise Exception(f"Failed to retrieve pinned links: {str(e)}")
    
    @staticmethod
    def get_link_stats() -> Dict[str, Any]:
        """
        Get statistics about links.
        
        Returns:
            Dict: Statistics including total links, pinned links, and links per category
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Get total links
            total_links = Link.query.count()
            
            # Get pinned links count
            pinned_links = Link.query.filter_by(pinned=True).count()
            
            # Get links count per category
            links_per_category = db.session.query(
                Category.name,
                db.func.count(Link.id).label('links_count')
            ).outerjoin(Link).group_by(Category.name).all()
            
            # Get uncategorized links count
            uncategorized_links = Link.query.filter_by(category_id=None).count()
            
            stats = {
                'total_links': total_links,
                'pinned_links': pinned_links,
                'uncategorized_links': uncategorized_links,
                'links_per_category': [
                    {
                        'category_name': cat.name or 'Uncategorized',
                        'links_count': cat.links_count
                    }
                    for cat in links_per_category
                ]
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Failed to get link statistics: {str(e)}") 