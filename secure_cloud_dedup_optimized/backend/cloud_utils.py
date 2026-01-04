"""
Cloud utilities for S3 integration
"""
import os
from .config import Config


# S3 Client Lazy-Loader
_s3_client_instance = None


def get_s3_client():
    """Lazy-load and return the S3 client"""
    global _s3_client_instance
    
    if not Config.USE_S3:
        return None
    
    if _s3_client_instance is None:
        try:
            import boto3
            _s3_client_instance = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY,
                aws_secret_access_key=Config.AWS_SECRET_KEY,
                region_name=Config.AWS_REGION
            )
        except Exception as e:
            print(f"Failed to initialize S3 client: {e}")
            return None
    
    return _s3_client_instance


def upload_to_s3(file_path, object_name):
    """
    Upload a file to S3 bucket
    
    Args:
        file_path: Local file path
        object_name: S3 object name
    
    Returns:
        bool: True if successful
    """
    s3 = get_s3_client()
    if not s3:
        return False
    
    try:
        s3.upload_file(file_path, Config.S3_BUCKET_NAME, object_name)
        return True
    except Exception as e:
        from botocore.exceptions import NoCredentialsError
        if isinstance(e, NoCredentialsError):
            print("AWS credentials not found.")
        else:
            print(f"S3 Upload Error: {e}")
        return False


def download_from_s3(object_name, local_path):
    """
    Download a file from S3 bucket
    
    Args:
        object_name: S3 object name
        local_path: Local file path
    
    Returns:
        bool: True if successful
    """
    s3 = get_s3_client()
    if not s3:
        return False
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(Config.S3_BUCKET_NAME, object_name, local_path)
        return True
    except Exception as e:
        print(f"S3 Download Error: {e}")
        return False


def delete_from_s3(object_name):
    """
    Delete a file from S3 bucket
    
    Args:
        object_name: S3 object name
    
    Returns:
        bool: True if successful
    """
    s3 = get_s3_client()
    if not s3:
        return False
    
    try:
        s3.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=object_name)
        return True
    except Exception as e:
        print(f"S3 Delete Error: {e}")
        return False


def list_s3_objects(prefix=''):
    """
    List objects in S3 bucket
    
    Args:
        prefix: Optional prefix filter
    
    Returns:
        List of object names
    """
    s3 = get_s3_client()
    if not s3:
        return []
    
    try:
        response = s3.list_objects_v2(
            Bucket=Config.S3_BUCKET_NAME,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except Exception as e:
        print(f"S3 List Error: {e}")
        return []
