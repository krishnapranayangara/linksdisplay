"""
Category model for organizing links into groups.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from marshmallow import Schema, fields, validate, ValidationError
from extensions import db

class Category(db.Model):
    """
    Category model for organizing links into logical groups.
    
    Attributes:
        id (int): Primary key, auto-incrementing
        name (str): Unique category name (max 100 characters)
        description (str): Optional description of the category
        created_at (datetime): Timestamp when category was created
        updated_at (datetime): Timestamp when category was last updated
        links (relationship): One-to-many relationship with Link model
    """
    
    __tablename__ = 'categories'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Category details
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    links = relationship('Link', back_populates='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the Category model."""
        return f'<Category(id={self.id}, name="{self.name}")>'
    
    def to_dict(self):
        """Convert category to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'links_count': len(self.links) if self.links else 0
        }
    
    @classmethod
    def find_by_name(cls, name):
        """Find a category by its name."""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_all_ordered(cls):
        """Get all categories ordered by name."""
        return cls.query.order_by(cls.name).all()
    
    def update(self, **kwargs):
        """Update category attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self

class CategorySchema(Schema):
    """
    Marshmallow schema for Category serialization/deserialization.
    
    Provides validation and data transformation for Category objects.
    """
    
    id = fields.Int(dump_only=True, description="Category ID")
    name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100),
        description="Category name (1-100 characters)"
    )
    description = fields.Str(
        validate=validate.Length(max=500),
        description="Optional category description (max 500 characters)"
    )
    created_at = fields.DateTime(dump_only=True, description="Creation timestamp")
    updated_at = fields.DateTime(dump_only=True, description="Last update timestamp")
    links_count = fields.Int(dump_only=True, description="Number of links in this category")
    
    class Meta:
        """Schema metadata."""
        ordered = True
        fields = ('id', 'name', 'description', 'created_at', 'updated_at', 'links_count')

# Schema instances for different use cases
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
category_create_schema = CategorySchema(exclude=('id', 'created_at', 'updated_at', 'links_count'))
category_update_schema = CategorySchema(exclude=('id', 'created_at', 'updated_at', 'links_count'), partial=True) 