"""
Link model for storing and managing bookmarks/links.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from marshmallow import Schema, fields, validate, ValidationError, validates
from urllib.parse import urlparse
from extensions import db

class Link(db.Model):
    """
    Link model for storing bookmarks and URLs with categorization.
    
    Attributes:
        id (int): Primary key, auto-incrementing
        title (str): Link title/name (max 200 characters)
        url (str): Full URL (max 500 characters)
        description (str): Optional description of the link
        category_id (int): Foreign key to Category model (nullable)
        pinned (bool): Whether the link is pinned/starred
        created_at (datetime): Timestamp when link was created
        updated_at (datetime): Timestamp when link was last updated
        category (relationship): Many-to-one relationship with Category model
    """
    
    __tablename__ = 'links'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Link details
    title = Column(String(200), nullable=False, index=True)
    url = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Category relationship
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Link status
    pinned = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship('Category', back_populates='links')
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_links_category_pinned', 'category_id', 'pinned'),
        Index('idx_links_created_at', 'created_at'),
    )
    
    def __repr__(self):
        """String representation of the Link model."""
        return f'<Link(id={self.id}, title="{self.title}", url="{self.url}")>'
    
    def to_dict(self):
        """Convert link to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'categoryId': self.category_id,
            'categoryName': self.category.name if self.category else None,
            'pinned': self.pinned,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def find_by_url(cls, url):
        """Find a link by its URL."""
        return cls.query.filter_by(url=url).first()
    
    @classmethod
    def get_by_category(cls, category_id):
        """Get all links for a specific category."""
        return cls.query.filter_by(category_id=category_id).order_by(cls.pinned.desc(), cls.created_at.desc()).all()
    
    @classmethod
    def get_pinned_links(cls):
        """Get all pinned links."""
        return cls.query.filter_by(pinned=True).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_by_title(cls, search_term):
        """Search links by title (case-insensitive)."""
        return cls.query.filter(cls.title.ilike(f'%{search_term}%')).all()
    
    def update(self, **kwargs):
        """Update link attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self
    
    def toggle_pin(self):
        """Toggle the pinned status of the link."""
        self.pinned = not self.pinned
        self.updated_at = datetime.utcnow()
        return self
    
    @staticmethod
    def validate_url(url):
        """
        Validate URL format.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

class LinkSchema(Schema):
    """
    Marshmallow schema for Link serialization/deserialization.
    
    Provides validation and data transformation for Link objects.
    """
    
    id = fields.Int(dump_only=True, description="Link ID")
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        description="Link title (1-200 characters)"
    )
    url = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500),
        description="Link URL (1-500 characters)"
    )
    description = fields.Str(
        validate=validate.Length(max=1000),
        description="Optional link description (max 1000 characters)"
    )
    categoryId = fields.Int(
        allow_none=True,
        attribute='category_id',
        description="Category ID (optional)"
    )
    categoryName = fields.Str(dump_only=True, description="Category name")
    pinned = fields.Bool(
        default=False,
        description="Whether the link is pinned"
    )
    createdAt = fields.DateTime(dump_only=True, description="Creation timestamp")
    updatedAt = fields.DateTime(dump_only=True, description="Last update timestamp")
    
    class Meta:
        """Schema metadata."""
        ordered = True
        fields = ('id', 'title', 'url', 'description', 'categoryId', 'categoryName', 'pinned', 'createdAt', 'updatedAt')
    
    @validates('url')
    def validate_url_format(self, value):
        """Custom URL validation."""
        if not Link.validate_url(value):
            raise ValidationError('Invalid URL format. Must include scheme (http/https) and domain.')
        return value

# Schema instances for different use cases
link_schema = LinkSchema()
links_schema = LinkSchema(many=True)
link_create_schema = LinkSchema(exclude=('id', 'createdAt', 'updatedAt', 'categoryName'))
link_update_schema = LinkSchema(exclude=('id', 'createdAt', 'updatedAt', 'categoryName'), partial=True) 