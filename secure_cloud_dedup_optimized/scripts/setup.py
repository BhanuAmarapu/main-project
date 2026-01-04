"""
Setup script for initializing the secure cloud deduplication system
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from database.db_manager import DatabaseManager
from backend.models import db
from backend.app import app


def setup_system():
    """Initialize the system"""
    print("=" * 60)
    print("Secure Cloud Deduplication System - Setup")
    print("=" * 60)
    
    # Create directories
    print("\n1. Creating directories...")
    Config.init_app()
    print("   ✓ Directories created")
    
    # Initialize database
    print("\n2. Initializing database...")
    with app.app_context():
        db.create_all()
        
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        print("   ✓ Database initialized")
        
        # Create admin user
        print("\n3. Creating admin user...")
        db_manager.create_admin_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("   ✓ Admin user created")
        print("      Username: admin")
        print("      Password: admin123")
    
    # Create .env file if it doesn't exist
    print("\n4. Checking environment configuration...")
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_example = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.example')
    
    if not os.path.exists(env_file) and os.path.exists(env_example):
        import shutil
        shutil.copy(env_example, env_file)
        print("   ✓ Created .env file from .env.example")
        print("   ⚠ Please edit .env with your configuration")
    elif os.path.exists(env_file):
        print("   ✓ .env file exists")
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env file with your configuration (if needed)")
    print("2. Run: python run.py")
    print("3. Open browser: http://127.0.0.1:5000")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    setup_system()
