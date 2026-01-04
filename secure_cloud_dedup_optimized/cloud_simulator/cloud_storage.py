"""
Cloud storage simulator
Simulates cloud storage with bandwidth and latency
"""
import time
import random
from backend.cloud_utils import upload_to_s3, download_from_s3, delete_from_s3
from backend.config import Config


class CloudStorageSimulator:
    """Simulate cloud storage with realistic delays"""
    
    def __init__(self, simulate_latency=True, simulate_bandwidth=True):
        """
        Initialize cloud storage simulator
        
        Args:
            simulate_latency: Simulate network latency
            simulate_bandwidth: Simulate bandwidth limits
        """
        self.simulate_latency = simulate_latency
        self.simulate_bandwidth = simulate_bandwidth
        
        # Simulation parameters
        self.base_latency_ms = 50  # 50ms base latency
        self.latency_variance_ms = 20  # ±20ms variance
        self.bandwidth_mbps = 10  # 10 Mbps upload/download speed
    
    def _simulate_delay(self, file_size_bytes):
        """
        Calculate simulated delay
        
        Args:
            file_size_bytes: Size of file in bytes
        
        Returns:
            Delay in seconds
        """
        delay = 0
        
        # Add latency
        if self.simulate_latency:
            latency = (self.base_latency_ms + random.uniform(-self.latency_variance_ms, self.latency_variance_ms)) / 1000
            delay += latency
        
        # Add bandwidth delay
        if self.simulate_bandwidth:
            file_size_mb = file_size_bytes / (1024 * 1024)
            transfer_time = file_size_mb / self.bandwidth_mbps
            delay += transfer_time
        
        return delay
    
    def upload(self, file_path, object_name):
        """
        Upload file to cloud with simulation
        
        Args:
            file_path: Local file path
            object_name: Cloud object name
        
        Returns:
            dict with upload result
        """
        import os
        
        start_time = time.time()
        file_size = os.path.getsize(file_path)
        
        # Simulate delay
        if self.simulate_latency or self.simulate_bandwidth:
            delay = self._simulate_delay(file_size)
            time.sleep(delay)
        
        # Actual upload (if S3 enabled)
        success = False
        if Config.USE_S3:
            success = upload_to_s3(file_path, object_name)
        else:
            # Simulate success
            success = True
        
        upload_time = time.time() - start_time
        
        return {
            'success': success,
            'file_size': file_size,
            'upload_time': upload_time,
            'speed_mbps': (file_size / (1024 * 1024)) / upload_time if upload_time > 0 else 0
        }
    
    def download(self, object_name, local_path):
        """
        Download file from cloud with simulation
        
        Args:
            object_name: Cloud object name
            local_path: Local file path
        
        Returns:
            dict with download result
        """
        import os
        
        start_time = time.time()
        
        # Actual download (if S3 enabled)
        success = False
        if Config.USE_S3:
            success = download_from_s3(object_name, local_path)
        else:
            # Simulate success
            success = True
        
        # Simulate delay
        if success and os.path.exists(local_path):
            file_size = os.path.getsize(local_path)
            if self.simulate_latency or self.simulate_bandwidth:
                delay = self._simulate_delay(file_size)
                time.sleep(delay)
        else:
            file_size = 0
        
        download_time = time.time() - start_time
        
        return {
            'success': success,
            'file_size': file_size,
            'download_time': download_time,
            'speed_mbps': (file_size / (1024 * 1024)) / download_time if download_time > 0 else 0
        }
    
    def delete(self, object_name):
        """
        Delete file from cloud
        
        Args:
            object_name: Cloud object name
        
        Returns:
            bool: Success status
        """
        if Config.USE_S3:
            return delete_from_s3(object_name)
        return True
    
    def set_bandwidth(self, mbps):
        """Set simulated bandwidth"""
        self.bandwidth_mbps = mbps
    
    def set_latency(self, base_ms, variance_ms):
        """Set simulated latency"""
        self.base_latency_ms = base_ms
        self.latency_variance_ms = variance_ms
    
    def get_stats(self):
        """Get simulator statistics"""
        return {
            'simulate_latency': self.simulate_latency,
            'simulate_bandwidth': self.simulate_bandwidth,
            'base_latency_ms': self.base_latency_ms,
            'latency_variance_ms': self.latency_variance_ms,
            'bandwidth_mbps': self.bandwidth_mbps,
            's3_enabled': Config.USE_S3
        }
