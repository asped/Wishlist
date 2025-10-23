#!/usr/bin/env python3
"""
Database Migration Script
Adds soft delete functionality to gifts table
"""

import sqlite3
import os

def migrate_database():
    """Add soft delete columns to gift table"""
    
    # Connect to the database
    db_path = 'instance/wishlist.db'
    if not os.path.exists(db_path):
        db_path = 'wishlist.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute('PRAGMA table_info(gift)')
        columns = [column[1] for column in cursor.fetchall()]
        
        print('Current gift table columns:', columns)
        
        # Add missing columns if they don't exist
        if 'is_deleted' not in columns:
            cursor.execute('ALTER TABLE gift ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
            print('Added is_deleted column')
        else:
            print('is_deleted column already exists')
        
        if 'deleted_at' not in columns:
            cursor.execute('ALTER TABLE gift ADD COLUMN deleted_at DATETIME')
            print('Added deleted_at column')
        else:
            print('deleted_at column already exists')
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print('Database migration completed successfully!')
        return True
        
    except Exception as e:
        print(f'Migration failed: {e}')
        return False

if __name__ == '__main__':
    migrate_database()
