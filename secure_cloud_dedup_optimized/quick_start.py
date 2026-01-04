"""
Simplified startup script - minimal dependencies
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Secure Cloud Deduplication System - Quick Start")
print("=" * 60)

# Check for required packages
required_packages = ['flask', 'flask_sqlalchemy', 'flask_login', 'werkzeug', 'cryptography']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"✓ {package} installed")
    except ImportError:
        print(f"✗ {package} NOT installed")
        missing_packages.append(package)

if missing_packages:
    print("\n" + "=" * 60)
    print("Missing packages detected!")
    print("=" * 60)
    print("\nPlease install missing packages:")
    print(f"pip install {' '.join(missing_packages)}")
    print("\nOr install all at once:")
    print("pip install flask flask-sqlalchemy flask-login werkzeug cryptography python-dotenv")
    sys.exit(1)

print("\n" + "=" * 60)
print("All dependencies installed! Starting application...")
print("=" * 60)

# Import and run the app
from backend.app import app, init_components, Config, db
from database.db_manager import DatabaseManager

# Initialize
Config.init_app()
print("✓ Directories initialized")

with app.app_context():
    db.create_all()
    
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print("✓ Database initialized")
    
    db_manager.create_admin_user()
    print("✓ Admin user created (username: admin, password: admin123)")
    
    init_components()
    print("✓ System components initialized")

print("\n" + "=" * 60)
print(f"Starting server at http://{Config.HOST}:{Config.PORT}")
print("=" * 60)
print("\nPress Ctrl+C to stop the server\n")

# Run application
app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
