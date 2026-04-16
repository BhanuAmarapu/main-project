"""
Test database connection for MySQL using mysql_wrapper
"""
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from mysql_wrapper import get_mysql_connection
import pymysql

print("=" * 60)
print("MySQL Database Connection Test")
print("=" * 60)

print(f"\nConnecting to MySQL:")
print(f"  Host: {Config.MYSQL_HOST}")
print(f"  User: {Config.MYSQL_USER}")
print(f"  DB:   {Config.MYSQL_DB}")

try:
    conn = get_mysql_connection()
    
    # Test query using mimic wrapper
    print("\n[OK] Connected successfully via mimic wrapper!")
    
    # Check tables
    # Since we're using the mimic, we can try to execute queries with '?'
    cursor = conn.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print(f"[OK] Found {len(tables)} tables")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check users table if exists
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]
        print(f"[OK] Users table has {users} users")
        
        # Try to fetch a user
        cursor = conn.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        if user:
            print(f"[OK] Sample user: {user['username']} (Role: {user['role']})")
    except Exception as e:
        print(f"[NOTE] 'users' table check skipped or failed: {e}")
    
    conn.close()
    print("\n[SUCCESS] MySQL Database is working correctly!")
    
except Exception as e:
    print(f"\n[ERROR] Database connection failed: {e}")
    print("\nTip: Make sure MySQL is running and the database 'cloud_dedup' exists.")
    print("     You can run 'python init_db.py' to initialize the database.")
    # import traceback
    # traceback.print_exc()
