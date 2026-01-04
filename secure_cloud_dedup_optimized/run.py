"""
Application entry point
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app, init_components, Config, db
from database.db_manager import DatabaseManager

if __name__ == '__main__':
    print("=" * 60)
    print("Secure Cloud Deduplication System - Optimized")
    print("=" * 60)
    
    # Initialize app directories
    Config.init_app()
    print("✓ Directories initialized")
    
    # Initialize database
    with app.app_context():
        db.create_all()
        
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        print("✓ Database initialized")
        
        # Create default admin user
        db_manager.create_admin_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✓ Admin user created (username: admin, password: admin123)")
        
        # Initialize components
        init_components()
        print("✓ System components initialized")
    
    print("\n" + "=" * 60)
    print(f"Starting server at http://{Config.HOST}:{Config.PORT}")
    print("=" * 60 + "\n")
    
    # Run application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
