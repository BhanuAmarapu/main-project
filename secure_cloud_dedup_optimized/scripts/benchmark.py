"""
Performance benchmarking script
"""
import os
import sys
import time
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.encryption import encrypt_file as traditional_encrypt
from backend.optimized_encryption import OptimizedEncryption


def create_test_file(size_mb):
    """Create a test file of specified size"""
    filepath = tempfile.mktemp(suffix='.bin')
    
    # Create file with random data
    with open(filepath, 'wb') as f:
        # Write in chunks to avoid memory issues
        chunk_size = 1024 * 1024  # 1MB chunks
        for _ in range(size_mb):
            f.write(os.urandom(chunk_size))
    
    return filepath


def benchmark_encryption():
    """Benchmark encryption performance"""
    print("=" * 60)
    print("Encryption Performance Benchmark")
    print("=" * 60)
    
    test_sizes = [1, 5, 10]  # MB
    
    for size_mb in test_sizes:
        print(f"\nTesting with {size_mb}MB file...")
        
        # Create test file
        test_file = create_test_file(size_mb)
        
        # Test traditional encryption
        print("  Traditional encryption...")
        trad_output = tempfile.mktemp(suffix='.enc')
        trad_start = time.time()
        traditional_encrypt(test_file, trad_output)
        trad_time = time.time() - trad_start
        print(f"    Time: {trad_time:.3f}s")
        print(f"    Speed: {size_mb / trad_time:.2f} MB/s")
        
        # Test optimized encryption
        print("  Optimized encryption...")
        opt_encryptor = OptimizedEncryption()
        opt_output = tempfile.mktemp(suffix='.enc')
        opt_stats = opt_encryptor.encrypt_file(test_file, opt_output)
        print(f"    Time: {opt_stats['time_seconds']:.3f}s")
        print(f"    Speed: {opt_stats['speed_mbps']:.2f} MB/s")
        print(f"    Chunks: {opt_stats['chunks']}")
        
        # Calculate speedup
        speedup = trad_time / opt_stats['time_seconds']
        print(f"  Speedup: {speedup:.2f}x")
        
        # Cleanup
        os.remove(test_file)
        os.remove(trad_output)
        os.remove(opt_output)
    
    print("\n" + "=" * 60)
    print("Benchmark completed!")
    print("=" * 60)


if __name__ == '__main__':
    Config.init_app()
    benchmark_encryption()
