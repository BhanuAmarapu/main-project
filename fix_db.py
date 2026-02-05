import sqlite3
import os

# Path to the database in the actual running directory
DB_PATH = r'C:\Users\amara\Desktop\Bhanu_03\main-project-main\db\cloud.db'
SCHEMA_PATH = r'C:\Users\amara\Desktop\Bhanu_03\main-project-main\db\schema.sql'

def init_db():
    # Ensure db directory exists
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Read and execute schema
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        print(f"Database initialized at {DB_PATH}")
        
        # Verify tables were created
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables created: {[t[0] for t in tables]}")

if __name__ == "__main__":
    init_db()
