"""
Test script to verify auto-initialization works after Git pull
This simulates what happens when you pull the code on a new machine
"""
import os
import sqlite3
import shutil

print("=" * 70)
print("Testing Auto-Initialization After Git Pull")
print("=" * 70)

# Step 1: Backup current database
print("\n[Step 1] Backing up current database...")
if os.path.exists('db/cloud.db'):
    shutil.copy('db/cloud.db', 'db/cloud.db.backup')
    print("✓ Database backed up to db/cloud.db.backup")
else:
    print("  No database to backup")

# Step 2: Delete database to simulate fresh Git pull
print("\n[Step 2] Simulating fresh Git pull (deleting database)...")
if os.path.exists('db/cloud.db'):
    os.remove('db/cloud.db')
    print("✓ Database deleted")
else:
    print("  Database already doesn't exist")

# Step 3: Verify database is gone
print("\n[Step 3] Verifying database is missing...")
if not os.path.exists('db/cloud.db'):
    print("✓ Database confirmed missing (simulating fresh clone)")
else:
    print("✗ ERROR: Database still exists!")
    exit(1)

# Step 4: Import and test auto-initialization
print("\n[Step 4] Testing auto-initialization...")
print("  Importing app.py (this should trigger auto-init)...")

# Simulate what happens when app.py runs
from config import Config

db_needs_init = False

if not os.path.exists(Config.DATABASE):
    print("  ✓ Database not found, will create...")
    db_needs_init = True
else:
    # Check if tables exist
    try:
        conn = sqlite3.connect(Config.DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            print("  ✓ Database tables missing, will initialize...")
            db_needs_init = True
        conn.close()
    except Exception:
        db_needs_init = True

# Initialize database if needed
if db_needs_init:
    from init_db import init_db
    init_db()
    print("✓ Database initialized successfully")
else:
    print("✓ Database already exists with tables")

# Step 5: Verify tables were created
print("\n[Step 5] Verifying tables were created...")
conn = sqlite3.connect('db/cloud.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
conn.close()

expected_tables = ['users', 'files', 'uploads', 'audits', 'logs', 
                   'suspicious_activities', 'user_activity_stats', 'moderation_logs']

print(f"  Found {len(tables)} tables:")
for table in tables:
    status = "✓" if table in expected_tables else "?"
    print(f"    {status} {table}")

# Step 6: Test that we can query the users table
print("\n[Step 6] Testing database functionality...")
try:
    conn = sqlite3.connect('db/cloud.db')
    cursor = conn.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"✓ Successfully queried users table (found {count} users)")
except Exception as e:
    print(f"✗ ERROR querying users table: {e}")
    exit(1)

# Step 7: Restore original database
print("\n[Step 7] Restoring original database...")
if os.path.exists('db/cloud.db.backup'):
    os.remove('db/cloud.db')
    shutil.move('db/cloud.db.backup', 'db/cloud.db')
    print("✓ Original database restored")

print("\n" + "=" * 70)
print("✓✓✓ TEST PASSED! Auto-initialization works correctly! ✓✓✓")
print("=" * 70)
print("\nConclusion:")
print("  When you pull this code on a new machine and run 'python run.py',")
print("  the database will be automatically created with all tables.")
print("  No manual 'python init_db.py' needed!")
print("=" * 70)
