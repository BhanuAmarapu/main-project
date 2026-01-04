"""
Setup script for Hybrid ML-CNS Deduplication System
This script initializes the database and prepares the system for first use
"""
import os
import sys
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def create_directories():
    """Create necessary directories"""
    directories = [
        Config.UPLOAD_FOLDER,
        Config.UPLOAD_TEMP,
        Config.STORAGE_PATH,
        os.path.dirname(Config.DATABASE),
        os.path.dirname(Config.ML_MODEL_PATH),
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")

def initialize_database():
    """Initialize the SQLite database with required tables"""
    print("\nInitializing database...")
    
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_hash TEXT UNIQUE NOT NULL,
            file_size INTEGER NOT NULL,
            stored_path TEXT NOT NULL,
            encryption_key TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create uploads table (tracks user-file relationships)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_id INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Create audits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            audit_result TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    conn.commit()
    print("✓ Database tables created successfully")
    
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
        conn.commit()
        print("✓ Default admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")
    
    conn.close()

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = {
        'flask': 'Flask',
        'werkzeug': 'Werkzeug',
        'flask_login': 'Flask-Login',
        'cryptography': 'Cryptography',
        'sklearn': 'Scikit-Learn',
        'boto3': 'Boto3 (optional for S3)'
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("=" * 60)
    print("Hybrid ML-CNS Deduplication System - Setup")
    print("=" * 60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Step 2: Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Step 3: Initialize database
    initialize_database()
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Configure AWS S3 credentials in config.py (optional)")
    print("2. Run the application: python run.py")
    print("3. Access at: http://127.0.0.1:5000")
    print("4. Login with: admin / admin123")
    print("=" * 60)

if __name__ == '__main__':
    main()
