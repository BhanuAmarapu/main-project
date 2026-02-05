"""
Main entry point for the Hybrid ML-CNS Deduplication System
Run this file to start the application: python run.py
"""
import os
import sys

# CRITICAL: Ensure we're in the correct directory and it's first in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# Add current directory to the BEGINNING of sys.path to ensure we import the correct app.py
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"[DEBUG] Working directory: {os.getcwd()}")
print(f"[DEBUG] Python will import from: {current_dir}")

# Import the main app (now guaranteed to be from current directory)
from app import app, get_db_connection, ml_model
from config import Config

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Hybrid ML-CNS Deduplication System...")
    print("=" * 60)
    
    # Check if model exists, only train if needed
    print("\n[1/3] Checking ML Model...")
    if os.path.exists(Config.ML_MODEL_PATH):
        print("[OK] ML Model found, skipping training")
    else:
        print("  Training new ML Model...")
        try:
            ml_model.train(Config.ML_DATASET)
            print("[OK] ML Model trained successfully")
        except Exception as e:
            print(f"[X] ML Model training failed: {e}")
            print("  Continuing without ML predictions...")
    
    print("\n[2/3] Initializing database...")
    try:
        conn = get_db_connection()
        conn.close()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[X] Database error: {e}")
        print("  Please run: python init_db.py")
        sys.exit(1)
    
    print("\n[3/3] Starting Flask server...")
    print("=" * 60)
    print(">>> Server starting on http://127.0.0.1:5000")
    print("    Press CTRL+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print("\n[ERROR] Port 5000 is already in use!")
            print("        Please stop other Python processes and try again.")
            print("        Run: Stop-Process -Name python -Force")
        else:
            print(f"\n[ERROR] {e}")
    except KeyboardInterrupt:
        print("\n\nGoodbye! Server stopped by user")
