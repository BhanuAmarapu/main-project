"""
Database manager for connection pooling and operations
"""
import sqlite3
import os
from backend.config import Config


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_path=None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self._connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
        return self._connection
    
    def close_connection(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute_query(self, query, params=None):
        """
        Execute a query
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            Cursor object
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        return cursor
    
    def execute_script(self, script):
        """
        Execute SQL script
        
        Args:
            script: SQL script
        """
        conn = self.get_connection()
        conn.executescript(script)
        conn.commit()
    
    def initialize_database(self):
        """Initialize database with schema"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            self.execute_script(schema)
            print("Database initialized successfully")
        else:
            print(f"Schema file not found: {schema_path}")
    
    def create_admin_user(self, username='admin', email='admin@example.com', password='admin123'):
        """
        Create default admin user
        
        Args:
            username: Admin username
            email: Admin email
            password: Admin password
        """
        from werkzeug.security import generate_password_hash
        
        password_hash = generate_password_hash(password)
        
        try:
            self.execute_query(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, 'admin')
            )
            print(f"Admin user created: {username}")
        except sqlite3.IntegrityError:
            print(f"Admin user already exists: {username}")
    
    def get_stats(self):
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        tables = ['users', 'files', 'uploads', 'blocks', 'ownerships', 
                  'performance_metrics', 'audit_logs', 'kek_tree_nodes']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count
        
        # Database file size
        if os.path.exists(self.db_path):
            stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        else:
            stats['database_size_mb'] = 0
        
        return stats
