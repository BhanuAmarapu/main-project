"""
Optimized Proof of Ownership (PoW) manager with adaptive difficulty
"""
import hashlib
import time
import random
from .models import db, Ownership, PerformanceMetric
from .config import Config
import json


class ProofOfWorkManager:
    """Optimized PoW manager with adaptive difficulty"""
    
    def __init__(self, difficulty=None, adaptive=None):
        """
        Initialize PoW manager
        
        Args:
            difficulty: Number of leading zeros required (default: from config)
            adaptive: Enable adaptive difficulty (default: from config)
        """
        self.difficulty = difficulty or Config.POW_DIFFICULTY
        self.adaptive = adaptive if adaptive is not None else Config.POW_ADAPTIVE
        self.challenge_cache = {}  # Cache for active challenges
        self.performance_history = []  # Track solve times for adaptation
    
    def generate_challenge(self, user_id, file_hash):
        """
        Generate a PoW challenge for ownership verification
        
        Args:
            user_id: User ID
            file_hash: File hash to verify ownership
        
        Returns:
            dict with challenge data
        """
        # Generate random challenge data
        nonce = random.randint(0, 1000000)
        timestamp = int(time.time())
        
        challenge_data = f"{user_id}:{file_hash}:{nonce}:{timestamp}"
        challenge_hash = hashlib.sha256(challenge_data.encode()).hexdigest()
        
        # Store challenge
        challenge_key = f"{user_id}:{file_hash}"
        self.challenge_cache[challenge_key] = {
            'challenge_hash': challenge_hash,
            'nonce': nonce,
            'timestamp': timestamp,
            'difficulty': self.difficulty,
            'file_hash': file_hash
        }
        
        return {
            'challenge_hash': challenge_hash,
            'difficulty': self.difficulty,
            'nonce': nonce,
            'timestamp': timestamp
        }
    
    def verify_proof(self, user_id, file_hash, proof_nonce):
        """
        Verify PoW solution
        
        Args:
            user_id: User ID
            file_hash: File hash
            proof_nonce: Nonce found by user
        
        Returns:
            dict with verification result
        """
        start_time = time.time()
        
        challenge_key = f"{user_id}:{file_hash}"
        
        if challenge_key not in self.challenge_cache:
            return {
                'success': False,
                'error': 'No active challenge found'
            }
        
        challenge = self.challenge_cache[challenge_key]
        
        # Reconstruct proof
        proof_data = f"{challenge['challenge_hash']}:{proof_nonce}"
        proof_hash = hashlib.sha256(proof_data.encode()).hexdigest()
        
        # Check if proof meets difficulty requirement
        required_prefix = '0' * challenge['difficulty']
        is_valid = proof_hash.startswith(required_prefix)
        
        verification_time = time.time() - start_time
        
        if is_valid:
            # Record ownership
            ownership = Ownership(
                user_id=user_id,
                file_id=None,  # Will be set by caller
                challenge_hash=challenge['challenge_hash'],
                response_hash=proof_hash,
                verification_method='pow'
            )
            
            db.session.add(ownership)
            
            # Record performance metric
            metric = PerformanceMetric(
                metric_type='pow_verification',
                metric_value=verification_time,
                metric_unit='seconds',
                metadata=json.dumps({
                    'difficulty': challenge['difficulty'],
                    'proof_hash': proof_hash
                })
            )
            db.session.add(metric)
            db.session.commit()
            
            # Update performance history for adaptive difficulty
            if self.adaptive:
                self.performance_history.append(verification_time)
                self._adapt_difficulty()
            
            # Clean up challenge
            del self.challenge_cache[challenge_key]
            
            return {
                'success': True,
                'verification_time': verification_time,
                'proof_hash': proof_hash,
                'ownership_id': ownership.id
            }
        else:
            return {
                'success': False,
                'error': 'Invalid proof',
                'expected_prefix': required_prefix,
                'got_hash': proof_hash
            }
    
    def _adapt_difficulty(self):
        """Adapt difficulty based on recent performance"""
        if len(self.performance_history) < 10:
            return  # Not enough data
        
        # Calculate average solve time from last 10 attempts
        recent_times = self.performance_history[-10:]
        avg_time = sum(recent_times) / len(recent_times)
        
        # Target solve time: 2-5 seconds
        target_min = 2.0
        target_max = 5.0
        
        if avg_time < target_min and self.difficulty < Config.POW_MAX_DIFFICULTY:
            # Too fast, increase difficulty
            self.difficulty += 1
            print(f"PoW difficulty increased to {self.difficulty}")
        elif avg_time > target_max and self.difficulty > Config.POW_MIN_DIFFICULTY:
            # Too slow, decrease difficulty
            self.difficulty -= 1
            print(f"PoW difficulty decreased to {self.difficulty}")
        
        # Keep only recent history
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]
    
    def solve_challenge(self, challenge_hash, difficulty, max_iterations=1000000):
        """
        Solve PoW challenge (for testing/simulation)
        
        Args:
            challenge_hash: Challenge hash to solve
            difficulty: Required difficulty
            max_iterations: Maximum attempts
        
        Returns:
            dict with solution or None
        """
        start_time = time.time()
        required_prefix = '0' * difficulty
        
        for nonce in range(max_iterations):
            proof_data = f"{challenge_hash}:{nonce}"
            proof_hash = hashlib.sha256(proof_data.encode()).hexdigest()
            
            if proof_hash.startswith(required_prefix):
                solve_time = time.time() - start_time
                return {
                    'nonce': nonce,
                    'proof_hash': proof_hash,
                    'iterations': nonce + 1,
                    'solve_time': solve_time
                }
        
        return None  # Failed to solve
    
    def get_stats(self):
        """Get PoW statistics"""
        total_verifications = Ownership.query.filter_by(verification_method='pow').count()
        
        avg_time = 0
        if self.performance_history:
            avg_time = sum(self.performance_history) / len(self.performance_history)
        
        return {
            'current_difficulty': self.difficulty,
            'adaptive_enabled': self.adaptive,
            'total_verifications': total_verifications,
            'average_verification_time': round(avg_time, 3),
            'active_challenges': len(self.challenge_cache)
        }


class SimpleOwnershipVerifier:
    """Simple ownership verification without PoW (for testing)"""
    
    @staticmethod
    def verify_ownership(user_id, file_id, file_hash):
        """
        Simple ownership verification
        
        Args:
            user_id: User ID
            file_id: File ID
            file_hash: File hash
        
        Returns:
            bool: True if verified
        """
        # Check if user has uploaded this file
        from .models import Upload
        
        upload = Upload.query.filter_by(user_id=user_id, file_id=file_id).first()
        
        if upload:
            # Record ownership
            ownership = Ownership(
                user_id=user_id,
                file_id=file_id,
                verification_method='simple'
            )
            db.session.add(ownership)
            db.session.commit()
            return True
        
        return False
