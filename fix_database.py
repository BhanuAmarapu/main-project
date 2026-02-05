"""
Quick Fix for Database Initialization Issue
This script ensures the database is properly initialized before the Flask app starts.
"""
import sqlite3
import os
from pathlib import Path

# Get the correct paths
BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / 'db'
DB_PATH = DB_DIR / 'cloud.db'
SCHEMA_PATH = DB_DIR / 'schema.sql'

print("=" * 70)
print("DATABASE INITIALIZATION FIX")
print("=" * 70)

print(f"\nWorking directory: {BASE_DIR}")
print(f"Database path: {DB_PATH}")
print(f"Schema path: {SCHEMA_PATH}")

# Ensure db directory exists
if not DB_DIR.exists():
    print("\n[1/3] Creating db directory...")
    DB_DIR.mkdir(parents=True, exist_ok=True)
    print("  [OK] Directory created")
else:
    print("\n[1/3] Database directory exists")

# Check if database file exists
db_exists = DB_PATH.exists()
print(f"\n[2/3] Database file exists: {db_exists}")

# Initialize or verify database
print("\n[3/3] Initializing database tables...")
try:
    with sqlite3.connect(str(DB_PATH)) as conn:
        # Read and execute schema
        with open(str(SCHEMA_PATH), 'r') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        
        # Verify tables
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables if t[0] != 'sqlite_sequence']
        
        print(f"  [OK] Created/verified {len(table_names)} tables:")
        for table in table_names:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"      - {table}: {count} rows")
        
        # Check for users
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            print("\n[SETUP] No users found. Creating default admin user...")
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', 'admin123', 'admin')
            )
            conn.commit()
            print("  [OK] Default admin user created")
            print("      Username: admin")
            print("      Password: admin123")
            print("      Role: admin")
        else:
            print(f"\n[INFO] Database has {user_count} existing users")

except FileNotFoundError:
    print(f"  [ERROR] Schema file not found: {SCHEMA_PATH}")
    print("  Please ensure db/schema.sql exists")
    exit(1)
except Exception as e:
    print(f"  [ERROR] Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
print("[SUCCESS] Database is ready!")
print("=" * 70)
print("\nYou can now run: python run.py")
print()
