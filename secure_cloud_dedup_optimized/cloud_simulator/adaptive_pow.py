"""
Adaptive Proof of Work manager
Dynamically adjusts difficulty based on system load and performance
"""
from backend.pow_manager import ProofOfWorkManager
from backend.models import db, PerformanceMetric
from datetime import datetime, timedelta
import json


class AdaptivePowManager(ProofOfWorkManager):
    """Adaptive PoW with dynamic difficulty adjustment"""
    
    def __init__(self, difficulty=None, adaptive=True):
        """
        Initialize adaptive PoW manager
        
        Args:
            difficulty: Initial difficulty
            adaptive: Enable adaptive mode
        """
        super().__init__(difficulty, adaptive=True)
        self.load_threshold_high = 0.8  # 80% load
        self.load_threshold_low = 0.3   # 30% load
        self.recent_solve_times = []
        self.max_history = 20
    
    def get_system_load(self):
        """
        Estimate system load based on recent activity
        
        Returns:
            Load factor (0.0 to 1.0)
        """
        # Check recent uploads in last 5 minutes
        from backend.models import Upload
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        recent_uploads = Upload.query.filter(
            Upload.upload_date >= cutoff_time
        ).count()
        
        # Normalize to 0-1 range (assume max 100 uploads per 5 min = high load)
        load = min(recent_uploads / 100.0, 1.0)
        
        return load
    
    def adapt_difficulty_by_load(self):
        """Adapt difficulty based on system load"""
        load = self.get_system_load()
        
        if load > self.load_threshold_high:
            # High load - decrease difficulty to reduce computation
            if self.difficulty > self.POW_MIN_DIFFICULTY:
                self.difficulty -= 1
                print(f"High load ({load:.2f}): PoW difficulty decreased to {self.difficulty}")
        
        elif load < self.load_threshold_low:
            # Low load - increase difficulty for better security
            if self.difficulty < self.POW_MAX_DIFFICULTY:
                self.difficulty += 1
                print(f"Low load ({load:.2f}): PoW difficulty increased to {self.difficulty}")
    
    def record_solve_time(self, solve_time):
        """
        Record a solve time for adaptation
        
        Args:
            solve_time: Time taken to solve challenge (seconds)
        """
        self.recent_solve_times.append(solve_time)
        
        # Keep only recent history
        if len(self.recent_solve_times) > self.max_history:
            self.recent_solve_times = self.recent_solve_times[-self.max_history:]
        
        # Adapt based on solve times
        if len(self.recent_solve_times) >= 5:
            avg_time = sum(self.recent_solve_times[-5:]) / 5
            
            # Target: 2-5 seconds
            if avg_time < 2.0 and self.difficulty < self.POW_MAX_DIFFICULTY:
                self.difficulty += 1
                print(f"Fast solves ({avg_time:.2f}s): PoW difficulty increased to {self.difficulty}")
            elif avg_time > 5.0 and self.difficulty > self.POW_MIN_DIFFICULTY:
                self.difficulty -= 1
                print(f"Slow solves ({avg_time:.2f}s): PoW difficulty decreased to {self.difficulty}")
    
    def generate_challenge(self, user_id, file_hash):
        """
        Generate adaptive challenge
        
        Args:
            user_id: User ID
            file_hash: File hash
        
        Returns:
            Challenge data
        """
        # Adapt difficulty before generating challenge
        self.adapt_difficulty_by_load()
        
        # Generate challenge with current difficulty
        return super().generate_challenge(user_id, file_hash)
    
    def verify_proof(self, user_id, file_hash, proof_nonce):
        """
        Verify proof and record metrics
        
        Args:
            user_id: User ID
            file_hash: File hash
            proof_nonce: Proof nonce
        
        Returns:
            Verification result
        """
        result = super().verify_proof(user_id, file_hash, proof_nonce)
        
        if result['success']:
            # Record solve time for adaptation
            self.record_solve_time(result['verification_time'])
        
        return result
    
    def get_adaptive_stats(self):
        """Get adaptive PoW statistics"""
        base_stats = super().get_stats()
        
        system_load = self.get_system_load()
        avg_solve_time = sum(self.recent_solve_times) / len(self.recent_solve_times) if self.recent_solve_times else 0
        
        base_stats.update({
            'adaptive_mode': True,
            'system_load': round(system_load, 3),
            'recent_solve_times_count': len(self.recent_solve_times),
            'average_solve_time': round(avg_solve_time, 3),
            'load_threshold_high': self.load_threshold_high,
            'load_threshold_low': self.load_threshold_low
        })
        
        return base_stats
