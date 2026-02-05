"""
Database Migration Script for Content Moderation

Adds moderation_logs table to existing database.
"""

import sqlite3
import os
from datetime import datetime


def migrate_database():
    """Add moderation_logs table to existing database"""
    
    db_path = 'db/cloud.db'
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("[MIGRATION] Starting database migration for content moderation...")
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='moderation_logs'
        """)
        
        if cursor.fetchone():
            print("[INFO] moderation_logs table already exists. Skipping creation.")
        else:
            # Create moderation_logs table
            cursor.execute("""
                CREATE TABLE moderation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    violation_type TEXT NOT NULL,
                    violation_details TEXT,
                    confidence_score REAL,
                    flagged_keywords TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reviewed INTEGER DEFAULT 0,
                    reviewer_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("[SUCCESS] Created moderation_logs table")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_user 
            ON moderation_logs(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_timestamp 
            ON moderation_logs(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_moderation_reviewed 
            ON moderation_logs(reviewed)
        """)
        
        print("[SUCCESS] Created indexes")
        
        conn.commit()
        conn.close()
        
        print("[MIGRATION] Database migration completed successfully!")
        print(f"[INFO] Migration completed at {datetime.now()}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("="*60)
    print("Content Moderation Database Migration")
    print("="*60)
    migrate_database()
