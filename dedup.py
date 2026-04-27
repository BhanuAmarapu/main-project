import os
import pymysql
from config import Config
from utils import get_file_hash, encrypt_file, log_action, upload_to_s3

class Deduplicator:
    def __init__(self):
        pass
        self.stored_dir = Config.UPLOAD_STORED

    def process_file(self, temp_path, file_name, user_id):
        """
        Process an uploaded file: Hash -> Check Dedup -> Encrypt -> Store
        Returns (is_duplicate, file_id)
        """
        file_hash = get_file_hash(temp_path)
        file_size = os.path.getsize(temp_path)
        file_type = file_name.split('.')[-1] if '.' in file_name else 'unknown'

        # Check for deduplication
        from mysql_wrapper import get_mysql_connection
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, stored_path FROM files WHERE file_hash = ?", (file_hash,))
        existing_file = cursor.fetchone()

        if existing_file:
            # Duplicate found
            file_id = existing_file[0]
            log_action("Deduplication", f"Duplicate detected for {file_name} (Hash: {file_hash}). Referencing existing file ID: {file_id}")
            
            # Record the upload for this user
            cursor.execute("INSERT INTO uploads (user_id, file_id) VALUES (?, ?)", (user_id, file_id))
            conn.commit()
            conn.close()
            log_action("Deduplication Success", f"Duplicate detected for {file_name} (Hash: {file_hash}). Referencing existing file ID: {file_id}")
            return True, file_id
        else:
            # Unique file
            # Limit filename length to prevent Windows path issues (max 260 chars)
            # Keep hash (64 chars) + extension, limit original filename
            file_extension = os.path.splitext(file_name)[1]  # e.g., '.pdf'
            base_name = os.path.splitext(file_name)[0]  # filename without extension
            
            # Limit base name to 50 characters to keep total path under Windows limit
            max_base_length = 50
            if len(base_name) > max_base_length:
                base_name = base_name[:max_base_length]
            
            stored_file_name = f"{file_hash}_{base_name}{file_extension}"
            stored_path = os.path.join(self.stored_dir, stored_file_name)
            
            # Ensure stored directory exists
            if not os.path.exists(self.stored_dir):
                os.makedirs(self.stored_dir, exist_ok=True)
            
            # Encrypt and move to stored_files (local temp before S3)
            encrypt_file(temp_path, stored_path)
            
            # First insert into database with local path
            cursor.execute("""
                INSERT INTO files (file_name, file_hash, file_size, file_type, stored_path)
                VALUES (?, ?, ?, ?, ?)
            """, (file_name, file_hash, file_size, file_type, stored_path))
            
            file_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO uploads (user_id, file_id) VALUES (?, ?)", (user_id, file_id))
            
            conn.commit()
            conn.close()
            
            # Cloud Sync (Hybrid Approach) - ASYNCHRONOUS
            if Config.USE_S3:
                import threading
                def background_s3_upload(local_path, s3_obj_name, f_id, f_name):
                    try:
                        if upload_to_s3(local_path, s3_obj_name):
                            log_action("Cloud Sync", f"File {f_name} synced to S3 bucket.")
                            s3_path = f"s3://{Config.S3_BUCKET_NAME}/{s3_obj_name}"
                            
                            # Update DB
                            from mysql_wrapper import get_mysql_connection
                            bg_conn = get_mysql_connection()
                            bg_conn.execute("UPDATE files SET stored_path = ? WHERE id = ?", (s3_path, f_id))
                            bg_conn.commit()
                            bg_conn.close()
                            
                            # Remove local file to save space
                            if os.path.exists(local_path):
                                os.remove(local_path)
                        else:
                            log_action("Cloud Warning", f"S3 sync failed for {f_name}, using local storage.")
                    except Exception as e:
                        log_action("Cloud Error", f"S3 Error: {str(e)}")
                
                threading.Thread(target=background_s3_upload, args=(stored_path, stored_file_name, file_id, file_name)).start()
            else:
                log_action("Local Storage", f"S3 disabled, storing {file_name} locally.")
            
            log_action("Upload", f"New file stored: {file_name} (ID: {file_id})")
            return False, file_id

    def proof_of_ownership(self, user_id, file_hash):
        """Simulate Proof of Ownership (PoW)."""
        # In a real CNS system, this would involve a challenge-response
        # Here we verify the user has the file locally (simulated by having the hash)
        log_action("PoW Verified", f"User {user_id} verified ownership for file hash: {file_hash}")
        return True
