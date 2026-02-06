"""
Enhanced deduplication manager with ML integration and Bloom filters
"""
import os
import time
from .models import db, File, Upload, PerformanceMetric
from .encryption import get_file_hash
from .config import Config
import json
from difflib import SequenceMatcher


class DeduplicationManager:
    """Enhanced deduplication engine"""
    
    def __init__(self, bloom_filter=None, ml_model=None):
        """
        Initialize deduplication manager
        
        Args:
            bloom_filter: Optional Bloom filter for fast lookups
            ml_model: Optional ML model for duplicate prediction
        """
        self.bloom_filter = bloom_filter
        self.ml_model = ml_model
        self.stats = {
            'total_files': 0,
            'duplicates_found': 0,
            'space_saved': 0,
            'dedup_ratio': 0.0
        }
    
    def check_duplicate(self, file_hash):
        """
        Check if file is a duplicate
        
        Args:
            file_hash: SHA-256 hash of file
        
        Returns:
            tuple: (is_duplicate, file_id or None)
        """
        # First check Bloom filter for fast negative lookup
        if self.bloom_filter and not self.bloom_filter.contains(file_hash):
            return False, None
        
        # Check database for actual duplicate
        existing_file = File.query.filter_by(file_hash=file_hash).first()
        
        if existing_file:
            return True, existing_file.id
        
        return False, None
    
    def process_file(self, temp_path, file_name, user_id, use_optimized=False, prefer_s3=True):
        """
        Process uploaded file with deduplication
        
        Args:
            temp_path: Path to temporary uploaded file
            file_name: Original filename
            user_id: User ID
            use_optimized: Use optimized encryption
            prefer_s3: User preference for S3 storage (True) or local storage (False)
        
        Returns:
            dict with processing results
        """
        start_time = time.time()
        
        # Calculate file hash
        file_hash = get_file_hash(temp_path)
        file_size = os.path.getsize(temp_path)
        file_type = file_name.split('.')[-1] if '.' in file_name else 'unknown'
        
        # Check for duplicate
        is_duplicate, file_id = self.check_duplicate(file_hash)
        
        if is_duplicate:
            # Duplicate found - just create upload record
            existing_file = File.query.get(file_id)
            existing_file.reference_count += 1
            
            upload = Upload(
                user_id=user_id,
                file_id=file_id,
                was_duplicate=True,
                upload_time_ms=int((time.time() - start_time) * 1000)
            )
            
            db.session.add(upload)
            db.session.commit()
            
            # Update stats
            self.stats['duplicates_found'] += 1
            self.stats['space_saved'] += file_size
            
            # Record performance metric
            metric = PerformanceMetric(
                metric_type='deduplication',
                metric_value=1.0,
                metric_unit='duplicate',
                metadata=json.dumps({
                    'file_size': file_size,
                    'file_hash': file_hash
                })
            )
            db.session.add(metric)
            db.session.commit()
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                'success': True,
                'is_duplicate': True,
                'file_id': file_id,
                'space_saved': file_size,
                'processing_time': time.time() - start_time
            }
        
        else:
            # New unique file - encrypt and store
            from .encryption import encrypt_file
            from .optimized_encryption import OptimizedEncryption
            import io
            
            # Generate stored filename
            file_extension = os.path.splitext(file_name)[1]
            base_name = os.path.splitext(file_name)[0][:50]  # Limit length
            stored_file_name = f"{file_hash}_{base_name}{file_extension}"
            stored_path = os.path.join(Config.UPLOAD_DIR, stored_file_name)
            
            # Handle S3 upload if enabled
            cloud_path = None
            is_in_cloud = False
            
            # Encrypt file
            encryption_start = time.time()
            
            if Config.USE_S3 and Config.DIRECT_S3_UPLOAD and prefer_s3:
                # Direct S3 upload - encrypt to memory and upload without local storage
                from .cloud_utils import upload_fileobj_to_s3
                
                # Encrypt to a temporary in-memory buffer
                encrypted_buffer = io.BytesIO()
                
                if use_optimized:
                    encryptor = OptimizedEncryption()
                    # Read file content
                    with open(temp_path, 'rb') as f:
                        file_content = f.read()
                    # Encrypt to buffer
                    encrypted_data = encryptor.encrypt_data(file_content)
                    encrypted_buffer.write(encrypted_data)
                    encryption_method = 'optimized_convergent'
                    enc_stats = {'time_seconds': time.time() - encryption_start}
                else:
                    # Use standard encryption to buffer
                    with open(temp_path, 'rb') as f:
                        file_content = f.read()
                    
                    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                    from cryptography.hazmat.backends import default_backend
                    import hashlib
                    
                    # Derive key from file hash (convergent encryption)
                    key = hashlib.sha256(file_hash.encode()).digest()
                    iv = os.urandom(16)
                    
                    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                    encryptor = cipher.encryptor()
                    
                    # Pad data
                    from cryptography.hazmat.primitives import padding
                    padder = padding.PKCS7(128).padder()
                    padded_data = padder.update(file_content) + padder.finalize()
                    
                    # Encrypt
                    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                    
                    # Write IV + encrypted data to buffer
                    encrypted_buffer.write(iv)
                    encrypted_buffer.write(encrypted_data)
                    encryption_method = 'convergent'
                    enc_stats = {'time_seconds': time.time() - encryption_start}
                
                # Upload encrypted buffer directly to S3
                s3_object_name = stored_file_name
                encrypted_buffer.seek(0)
                
                if upload_fileobj_to_s3(encrypted_buffer, s3_object_name):
                    cloud_path = f"s3://{Config.S3_BUCKET_NAME}/{s3_object_name}"
                    is_in_cloud = True
                    print(f"✓ File uploaded directly to S3: {s3_object_name}")
                else:
                    # Fallback to local storage if S3 upload fails
                    print(f"⚠ S3 upload failed, falling back to local storage")
                    encrypted_buffer.seek(0)
                    with open(stored_path, 'wb') as f:
                        f.write(encrypted_buffer.read())
                
                encrypted_buffer.close()
                
            else:
                # Local storage or S3 disabled - encrypt to local file
                if use_optimized:
                    encryptor = OptimizedEncryption()
                    enc_stats = encryptor.encrypt_file(temp_path, stored_path)
                    encryption_method = 'optimized_convergent'
                else:
                    encrypt_file(temp_path, stored_path)
                    enc_stats = {'time_seconds': time.time() - encryption_start}
                    encryption_method = 'convergent'
                
                # Upload to S3 if enabled and user prefers S3 (but keep local copy)
                if Config.USE_S3 and prefer_s3 and not Config.SKIP_LOCAL_STORAGE:
                    from .cloud_utils import upload_to_s3
                    s3_object_name = stored_file_name
                    
                    if upload_to_s3(stored_path, s3_object_name):
                        cloud_path = f"s3://{Config.S3_BUCKET_NAME}/{s3_object_name}"
                        is_in_cloud = True
                        print(f"✓ File uploaded to S3 (local copy retained): {s3_object_name}")
            
            # Create file record
            new_file = File(
                file_name=file_name,
                file_hash=file_hash,
                file_size=file_size,
                file_type=file_type,
                stored_path=stored_path if not is_in_cloud else cloud_path,
                is_encrypted=True,
                encryption_method=encryption_method,
                reference_count=1,
                is_deduplicated=False,
                is_in_cloud=is_in_cloud,
                cloud_path=cloud_path
            )
            
            db.session.add(new_file)
            db.session.flush()
            
            # Create upload record
            upload = Upload(
                user_id=user_id,
                file_id=new_file.id,
                was_duplicate=False,
                upload_time_ms=int((time.time() - start_time) * 1000)
            )
            
            db.session.add(upload)
            
            # Add to Bloom filter
            if self.bloom_filter:
                self.bloom_filter.add(file_hash)
            
            # Record performance metrics
            enc_metric = PerformanceMetric(
                metric_type='encryption',
                metric_value=enc_stats['time_seconds'],
                metric_unit='seconds',
                metadata=json.dumps({
                    'method': encryption_method,
                    'file_size': file_size
                })
            )
            db.session.add(enc_metric)
            
            db.session.commit()
            
            # Update stats
            self.stats['total_files'] += 1
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                'success': True,
                'is_duplicate': False,
                'file_id': new_file.id,
                'encryption_time': enc_stats['time_seconds'],
                'processing_time': time.time() - start_time,
                'stored_in_cloud': is_in_cloud
            }
    
    def get_dedup_stats(self):
        """Get deduplication statistics"""
        total_files = File.query.count()
        total_uploads = Upload.query.count()
        duplicates = Upload.query.filter_by(was_duplicate=True).count()
        
        total_size = db.session.query(db.func.sum(File.file_size)).scalar() or 0
        unique_size = total_size
        
        if total_uploads > 0:
            # Calculate space saved from duplicates
            duplicate_uploads = Upload.query.filter_by(was_duplicate=True).all()
            space_saved = sum([File.query.get(u.file_id).file_size for u in duplicate_uploads if File.query.get(u.file_id)])
            
            dedup_ratio = (space_saved / (total_size + space_saved)) * 100 if (total_size + space_saved) > 0 else 0
        else:
            space_saved = 0
            dedup_ratio = 0
        
        return {
            'total_unique_files': total_files,
            'total_uploads': total_uploads,
            'duplicates_detected': duplicates,
            'space_saved_bytes': space_saved,
            'space_saved_mb': space_saved / (1024 * 1024),
            'deduplication_ratio': round(dedup_ratio, 2),
            'total_storage_bytes': total_size,
            'total_storage_mb': total_size / (1024 * 1024)
        }
    
    def predict_duplicate_ml(self, file_features):
        """
        Use ML model to predict if file is likely a duplicate
        
        Args:
            file_features: Feature vector for file
        
        Returns:
            Probability of being a duplicate
        """
        if self.ml_model is None:
            return 0.5  # No model, return neutral probability
        
        try:
            prediction = self.ml_model.predict_proba([file_features])[0][1]
            return prediction
        except Exception as e:
            print(f"ML prediction error: {e}")
            return 0.5
    
    def calculate_filename_similarity(self, name1, name2):
        """
        Calculate filename similarity using Levenshtein distance
        
        Args:
            name1: First filename
            name2: Second filename
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Normalize filenames (lowercase, remove extensions for comparison)
        base1 = os.path.splitext(name1.lower())[0]
        base2 = os.path.splitext(name2.lower())[0]
        
        return SequenceMatcher(None, base1, base2).ratio()
    
    def calculate_size_similarity(self, size1, size2):
        """
        Calculate file size similarity
        
        Args:
            size1: First file size in bytes
            size2: Second file size in bytes
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if size1 == 0 and size2 == 0:
            return 1.0
        
        max_size = max(size1, size2)
        min_size = min(size1, size2)
        
        if max_size == 0:
            return 0.0
        
        # Calculate percentage difference
        return min_size / max_size
    
    def calculate_similarity(self, file_name, file_size, file_type, existing_file):
        """
        Calculate overall similarity between uploaded file and existing file
        
        Args:
            file_name: Uploaded filename
            file_size: Uploaded file size
            file_type: Uploaded file type
            existing_file: Existing File object from database
        
        Returns:
            dict with similarity score and breakdown
        """
        # Calculate individual similarities
        filename_sim = self.calculate_filename_similarity(file_name, existing_file.file_name)
        size_sim = self.calculate_size_similarity(file_size, existing_file.file_size)
        type_match = 1.0 if file_type.lower() == existing_file.file_type.lower() else 0.0
        
        # Weighted average (filename: 40%, size: 30%, type: 20%, ML: 10%)
        # For now, ML prediction is set to 0.5 (neutral) if not available
        ml_score = 0.5
        if self.ml_model:
            try:
                features = self.extract_file_features(file_name, file_size, file_type)
                ml_score = self.predict_duplicate_ml(features)
            except:
                pass
        
        overall_similarity = (
            filename_sim * 0.4 +
            size_sim * 0.3 +
            type_match * 0.2 +
            ml_score * 0.1
        )
        
        return {
            'overall': round(overall_similarity * 100, 2),
            'filename': round(filename_sim * 100, 2),
            'size': round(size_sim * 100, 2),
            'type': round(type_match * 100, 2),
            'ml_prediction': round(ml_score * 100, 2)
        }
    
    def extract_file_features(self, file_name, file_size, file_type):
        """
        Extract features for ML model prediction
        
        Args:
            file_name: Filename
            file_size: File size in bytes
            file_type: File type/extension
        
        Returns:
            Feature vector for ML model
        """
        # Simple feature extraction (can be enhanced)
        features = [
            len(file_name),  # Filename length
            file_size,  # File size
            len(file_type),  # Extension length
            file_name.count('_'),  # Underscore count
            file_name.count('-'),  # Dash count
        ]
        return features
    
    def get_similar_files(self, file_name, file_size, file_type, file_hash, threshold=70.0):
        """
        Find similar files based on metadata and hash
        
        Args:
            file_name: Uploaded filename
            file_size: Uploaded file size
            file_type: Uploaded file type
            file_hash: File hash
            threshold: Minimum similarity percentage to return (default 70%)
        
        Returns:
            list of dicts with similar files and their similarity scores
        """
        similar_files = []
        
        # First check for exact hash match
        exact_match = File.query.filter_by(file_hash=file_hash).first()
        if exact_match:
            return [{
                'file': exact_match,
                'similarity': {
                    'overall': 100.0,
                    'filename': 100.0,
                    'size': 100.0,
                    'type': 100.0,
                    'ml_prediction': 100.0
                },
                'match_type': 'exact_hash'
            }]
        
        # Check for metadata-based similarity
        # Get files of the same type first for efficiency
        candidate_files = File.query.filter_by(file_type=file_type).all()
        
        for existing_file in candidate_files:
            similarity = self.calculate_similarity(file_name, file_size, file_type, existing_file)
            
            if similarity['overall'] >= threshold:
                similar_files.append({
                    'file': existing_file,
                    'similarity': similarity,
                    'match_type': 'ml_predicted'
                })
        
        # Sort by similarity (highest first)
        similar_files.sort(key=lambda x: x['similarity']['overall'], reverse=True)
        
        # Return top 5 most similar files
        return similar_files[:5]
    
    def check_duplicate_with_details(self, file_hash, file_name, file_size, file_type):
        """
        Enhanced duplicate check that returns detailed information
        
        Args:
            file_hash: SHA-256 hash of file
            file_name: Original filename
            file_size: File size in bytes
            file_type: File type/extension
        
        Returns:
            dict with duplicate status and similar files
        """
        similar_files = self.get_similar_files(file_name, file_size, file_type, file_hash)
        
        if not similar_files:
            return {
                'is_duplicate': False,
                'similar_files': []
            }
        
        # If we have similar files, return them
        return {
            'is_duplicate': True,
            'similar_files': similar_files
        }
