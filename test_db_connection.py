"""
Test database connection using the same method as app.py
"""
from config import Config
import sqlite3

print("=" * 60)
print("Database Connection Test")
print("=" * 60)

print(f"\nDatabase path from Config: {Config.DATABASE}")

try:
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Test query
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tables = [r[0] for r in result]
    
    print(f"\n[OK] Connected successfully!")
    print(f"[OK] Found {len(tables)} tables: {tables}")
    
    # Check users table
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"[OK] Users table has {users} users")
    
    # Try to fetch a user
    user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
    if user:
        print(f"[OK] Sample user: {dict(user)}")
    
    conn.close()
    print("\n[SUCCESS] Database is working correctly!")
    
except Exception as e:
    print(f"\n[ERROR] Database connection failed: {e}")
    import traceback
    traceback.print_exc()
