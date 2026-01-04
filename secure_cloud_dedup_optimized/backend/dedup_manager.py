"""
Enhanced deduplication manager with ML integration and Bloom filters
"""
import os
import time
from .models import db, File, Upload, PerformanceMetric
from .encryption import get_file_hash
from .config import Config
import json


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
    
    def process_file(self, temp_path, file_name, user_id, use_optimized=False):
        """
        Process uploaded file with deduplication
        
        Args:
            temp_path: Path to temporary uploaded file
            file_name: Original filename
            user_id: User ID
            use_optimized: Use optimized encryption
        
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
            
            # Generate stored filename
            file_extension = os.path.splitext(file_name)[1]
            base_name = os.path.splitext(file_name)[0][:50]  # Limit length
            stored_file_name = f"{file_hash}_{base_name}{file_extension}"
            stored_path = os.path.join(Config.UPLOAD_DIR, stored_file_name)
            
            # Encrypt file
            encryption_start = time.time()
            if use_optimized:
                encryptor = OptimizedEncryption()
                enc_stats = encryptor.encrypt_file(temp_path, stored_path)
                encryption_method = 'optimized_convergent'
            else:
                encrypt_file(temp_path, stored_path)
                enc_stats = {'time_seconds': time.time() - encryption_start}
                encryption_method = 'convergent'
            
            # Handle S3 upload if enabled
            cloud_path = None
            is_in_cloud = False
            
            if Config.USE_S3:
                from .cloud_utils import upload_to_s3
                s3_object_name = stored_file_name
                
                if upload_to_s3(stored_path, s3_object_name):
                    cloud_path = f"s3://{Config.S3_BUCKET_NAME}/{s3_object_name}"
                    is_in_cloud = True
                    
                    # Remove local copy if in cloud
                    if os.path.exists(stored_path):
                        os.remove(stored_path)
            
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
