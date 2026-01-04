import os
from pathlib import Path

# Try to load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("Note: python-dotenv not installed. Using environment variables or defaults.")
    print("      Install with: pip install python-dotenv")

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'secure-data-dedup-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    DATABASE = os.path.join(BASE_DIR, os.getenv('DATABASE_PATH', 'db/cloud.db'))
    
    # Upload folders
    UPLOAD_TEMP = os.path.join(BASE_DIR, 'uploads', 'temp_files')
    UPLOAD_STORED = os.path.join(BASE_DIR, 'uploads', 'stored_files')
    
    # ML Data
    ML_DATASET = os.path.join(BASE_DIR, 'ml_data', 'metadata_dataset.csv')
    ML_MODEL_PATH = os.path.join(BASE_DIR, 'ml_data', 'model.pkl')
    
    # Encryption
    AES_KEY = os.getenv('AES_KEY', 'Sixteen byte key').encode()
    
    # Audit Logs
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Cloud Storage (AWS S3)
    USE_S3 = os.getenv('USE_S3', 'False').lower() == 'true'  # Changed default to False for security
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')  # No default credentials
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')  # No default credentials
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
    
    # Auto-disable S3 if credentials are missing but it was enabled
    if USE_S3 and (not AWS_ACCESS_KEY or not AWS_SECRET_KEY):
        print("WARNING: USE_S3 is True but AWS credentials are missing. S3 will be disabled.")
        USE_S3 = False

# Ensure directories exist
for folder in [Config.UPLOAD_TEMP, Config.UPLOAD_STORED, Config.LOGS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)
