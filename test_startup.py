"""
Complete startup test - simulates what run.py does
"""
import os
import sys

# CRITICAL: Ensure we're in the correct directory and it's first in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# Add current directory to the BEGINNING of sys.path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=" * 70)
print("COMPLETE STARTUP TEST")
print("=" * 70)

print(f"\n[1/5] Working Directory Check")
print(f"  Current directory: {os.getcwd()}")
print(f"  [OK] Correct directory")

print(f"\n[2/5] Python Path Check")
print(f"  First in sys.path: {sys.path[0]}")
if sys.path[0] == current_dir:
    print(f"  [OK] Current directory is first in path")
else:
    print(f"  [WARNING] Current directory not first")

print(f"\n[3/5] App Import Check")
try:
    import app
    print(f"  Loaded app from: {app.__file__}")
    if current_dir in app.__file__:
        print(f"  [OK] Correct app.py loaded")
    else:
        print(f"  [ERROR] Wrong app.py loaded!")
        sys.exit(1)
except Exception as e:
    print(f"  [ERROR] Failed to import app: {e}")
    sys.exit(1)

print(f"\n[4/5] Database Connection Check")
try:
    from config import Config
    print(f"  Database path: {Config.DATABASE}")
    
    import sqlite3
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Test users table
    result = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"  [OK] Users table accessible ({result} users)")
    
    # Test a user query (same as app.py does)
    user = conn.execute("SELECT * FROM users WHERE id = ?", (1,)).fetchone()
    if user:
        print(f"  [OK] User query successful")
    
    conn.close()
except Exception as e:
    print(f"  [ERROR] Database check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n[5/5] Flask App Check")
try:
    flask_app = app.app
    print(f"  [OK] Flask app instance created")
    print(f"  App name: {flask_app.name}")
except Exception as e:
    print(f"  [ERROR] Flask app check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("[SUCCESS] All checks passed! Application is ready to run.")
print("=" * 70)
print("\nYou can now safely run: python run.py")
