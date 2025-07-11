#!/usr/bin/env python3
"""
Database initialization script for Link Organizer
Creates the database and tables if they don't exist
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'admin'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        db_name = os.getenv('DB_NAME', 'link_organizer')
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {db_name}')
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def init_tables():
    """Initialize tables using Flask app"""
    try:
        from app import app, db, Category
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully")
            
            # Add default categories
            default_categories = ['Work', 'Personal']
            for category_name in default_categories:
                existing = Category.query.filter_by(name=category_name).first()
                if not existing:
                    category = Category(name=category_name)
                    db.session.add(category)
                    print(f"✅ Added default category: {category_name}")
            
            db.session.commit()
            print("✅ Default categories added successfully")
            
    except Exception as e:
        print(f"❌ Error initializing tables: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Initializing Link Organizer Database...")
    
    # Create database
    create_database()
    
    # Initialize tables and default data
    init_tables()
    
    print("🎉 Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("1. Copy env.example to .env and update database credentials")
    print("2. Run: python app.py")
    print("3. API will be available at: http://localhost:5000/api") 