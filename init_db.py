import sqlite3
import os

DB_PATH = os.path.join('db', 'cloud.db')
SCHEMA_PATH = os.path.join('db', 'schema.sql')

def init_db():
    if not os.path.exists('db'):
        os.makedirs('db')
    
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
