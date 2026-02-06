"""
Configuration management for the secure cloud deduplication system
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'secure-data-dedup-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database Configuration
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Storage Directories
    STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
    UPLOAD_DIR = os.path.join(STORAGE_DIR, 'uploaded_files')
    BLOCKS_DIR = os.path.join(STORAGE_DIR, 'blocks')
    TEMP_DIR = os.path.join(STORAGE_DIR, 'temp')
    CACHE_DIR = os.path.join(STORAGE_DIR, 'cache')
    COMPRESSED_DIR = os.path.join(STORAGE_DIR, 'compressed')
    
    # Logs Directory
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Reports Directory
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    
    # AWS S3 Configuration
    USE_S3 = os.getenv('USE_S3', 'False').lower() == 'true'
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
    
    # S3 Direct Upload Configuration (from config.yaml)
    DIRECT_S3_UPLOAD = True  # Upload directly to S3 without local storage
    SKIP_LOCAL_STORAGE = True  # Don't save files locally when S3 is enabled
    
    # Encryption Configuration
    AES_KEY = os.getenv('AES_KEY', 'Sixteen byte key').encode()
    ENCRYPTION_SALT = b'salt_secure_dedup_2024'
    
    # Performance Configuration
    CHUNK_SIZE = 4096  # 4KB chunks for file processing
    PARALLEL_WORKERS = int(os.getenv('PARALLEL_WORKERS', 4))
    ENABLE_COMPRESSION = os.getenv('ENABLE_COMPRESSION', 'True').lower() == 'true'
    
    # Bloom Filter Configuration
    BLOOM_FILTER_SIZE = 1000000  # 1M bits
    BLOOM_FILTER_HASH_COUNT = 7
    BLOOM_FILTER_FALSE_POSITIVE_RATE = 0.01
    
    # PoW Configuration
    POW_DIFFICULTY = int(os.getenv('POW_DIFFICULTY', 4))
    POW_ADAPTIVE = os.getenv('POW_ADAPTIVE', 'True').lower() == 'true'
    POW_MIN_DIFFICULTY = 2
    POW_MAX_DIFFICULTY = 6
    
    # Block-level Deduplication
    BLOCK_SIZE = 4096  # 4KB blocks
    USE_VARIABLE_BLOCKS = os.getenv('USE_VARIABLE_BLOCKS', 'False').lower() == 'true'
    
    # Cache Configuration
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_MAX_SIZE = 1000  # Maximum number of cached items
    CACHE_TTL = 3600  # Time to live in seconds (1 hour)
    
    # Upload Configuration
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'csv', 'json'}
    
    # ML Configuration
    ML_MODEL_PATH = os.path.join(BASE_DIR, 'ml_model.pkl')
    ML_ENABLED = os.getenv('ML_ENABLED', 'True').lower() == 'true'
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        directories = [
            Config.STORAGE_DIR,
            Config.UPLOAD_DIR,
            Config.BLOCKS_DIR,
            Config.TEMP_DIR,
            Config.CACHE_DIR,
            Config.COMPRESSED_DIR,
            Config.LOGS_DIR,
            Config.REPORTS_DIR,
            os.path.join(Config.REPORTS_DIR, 'comparison_charts'),
            os.path.join(Config.REPORTS_DIR, 'test_results'),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Create database directory
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
