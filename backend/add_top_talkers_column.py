#!/usr/bin/env python3
"""
Add top_talkers column to traffic_stats table
Run with: python add_top_talkers_column.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text, inspect

def add_column():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if table exists
        if 'traffic_stats' not in inspector.get_table_names():
            print("❌ traffic_stats table doesn't exist yet")
            return
        
        # Check if column already exists
        columns = [c['name'] for c in inspector.get_columns('traffic_stats')]
        
        if 'top_talkers' in columns:
            print("✅ top_talkers column already exists")
            return
        
        # Add the column
        print("Adding top_talkers column...")
        try:
            db.session.execute(text('ALTER TABLE traffic_stats ADD COLUMN top_talkers JSON'))
            db.session.commit()
            print("✅ top_talkers column added successfully!")
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_column()
