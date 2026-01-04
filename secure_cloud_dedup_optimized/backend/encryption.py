"""
Traditional convergent encryption module
"""
import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from .config import Config


def get_file_hash(file_path):
    """Generate SHA-256 hash for a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(Config.CHUNK_SIZE), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_string_hash(data):
    """Generate SHA-256 hash for a string"""
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def derive_key_from_content(file_path):
    """Derive encryption key from file content (convergent encryption)"""
    file_hash = get_file_hash(file_path)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=Config.ENCRYPTION_SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(file_hash.encode()))
    return key


def derive_key_from_password(password):
    """Derive encryption key from password"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=Config.ENCRYPTION_SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password if isinstance(password, bytes) else password.encode()))
    return key


def encrypt_file(file_path, output_path, key=None):
    """
    Encrypt file using Fernet (AES)
    
    Args:
        file_path: Path to input file
        output_path: Path to output encrypted file
        key: Optional encryption key (if None, derives from content)
    
    Returns:
        Encryption key used
    """
    if key is None:
        # Convergent encryption: derive key from file content
        key = derive_key_from_content(file_path)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    fernet = Fernet(key)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    encrypted_data = fernet.encrypt(data)
    
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    
    return key


def decrypt_file(file_path, output_path, key=None, original_file_path=None):
    """
    Decrypt file using Fernet (AES)
    
    Args:
        file_path: Path to encrypted file
        output_path: Path to output decrypted file
        key: Optional decryption key
        original_file_path: Path to original file (for convergent encryption)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if key is None and original_file_path:
            # Convergent encryption: derive key from original file
            key = derive_key_from_content(original_file_path)
        elif key is None:
            # Use default key
            key = derive_key_from_password(Config.AES_KEY)
        
        fernet = Fernet(key)
        
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        return True
    except Exception as e:
        print(f"Decryption error: {e}")
        return False


def encrypt_data(data, key=None):
    """
    Encrypt data bytes
    
    Args:
        data: Bytes to encrypt
        key: Optional encryption key
    
    Returns:
        Encrypted bytes
    """
    if key is None:
        key = derive_key_from_password(Config.AES_KEY)
    
    fernet = Fernet(key)
    return fernet.encrypt(data)


def decrypt_data(encrypted_data, key=None):
    """
    Decrypt data bytes
    
    Args:
        encrypted_data: Encrypted bytes
        key: Optional decryption key
    
    Returns:
        Decrypted bytes
    """
    if key is None:
        key = derive_key_from_password(Config.AES_KEY)
    
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)


class ConvergentEncryption:
    """Convergent encryption handler"""
    
    def __init__(self):
        self.salt = Config.ENCRYPTION_SALT
    
    def encrypt_file(self, input_path, output_path):
        """Encrypt file with convergent encryption"""
        return encrypt_file(input_path, output_path)
    
    def decrypt_file(self, encrypted_path, output_path, original_path=None):
        """Decrypt file with convergent encryption"""
        return decrypt_file(encrypted_path, output_path, original_file_path=original_path)
    
    def get_file_hash(self, file_path):
        """Get file hash"""
        return get_file_hash(file_path)
