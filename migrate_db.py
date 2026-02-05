"""
Database Migration Script
Adds content_text column to uploads table for content similarity detection
"""
import sqlite3
import os

DB_PATH = os.path.join('db', 'cloud.db')

def migrate_database():
    """Add content_text column to uploads table"""
    print("Starting database migration...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run init_db.py first")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(uploads)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'content_text' in columns:
            print("✓ Column 'content_text' already exists in uploads table")
            conn.close()
            return True
        
        # Add the column
        print("Adding 'content_text' column to uploads table...")
        cursor.execute("""
            ALTER TABLE uploads 
            ADD COLUMN content_text TEXT
        """)
        
        conn.commit()
        print("✓ Migration completed successfully!")
        print("  - Added 'content_text' column to uploads table")
        print("  - Existing records will have NULL values (content similarity will work for new uploads)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n✓ Database is ready for content similarity detection!")
    else:
        print("\n✗ Migration failed. Please check the error above.")
