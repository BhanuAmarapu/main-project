"""
Test deduplication functionality
"""
import os
import sys
import tempfile
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.dedup_manager import DeduplicationManager
from cloud_simulator.optimized_bloom_filter import OptimizedBloomFilter
from backend.models import db
from backend.app import app


def create_test_file(content, filename):
    """Create a test file with given content"""
    filepath = os.path.join(Config.TEMP_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


def test_deduplication():
    """Test deduplication functionality"""
    print("=" * 60)
    print("Testing Deduplication Functionality")
    print("=" * 60)
    
    with app.app_context():
        # Initialize components
        bloom_filter = OptimizedBloomFilter()
        dedup_manager = DeduplicationManager(bloom_filter=bloom_filter)
        
        # Test 1: Upload unique file
        print("\nTest 1: Uploading unique file...")
        file1 = create_test_file("This is test content 1", "test1.txt")
        result1 = dedup_manager.process_file(file1, "test1.txt", user_id=1)
        
        if result1['success'] and not result1['is_duplicate']:
            print("   ✓ Unique file uploaded successfully")
        else:
            print("   ✗ Test failed")
        
        # Test 2: Upload duplicate file
        print("\nTest 2: Uploading duplicate file...")
        file2 = create_test_file("This is test content 1", "test2.txt")
        result2 = dedup_manager.process_file(file2, "test2.txt", user_id=1)
        
        if result2['success'] and result2['is_duplicate']:
            print("   ✓ Duplicate detected successfully")
            print(f"   Space saved: {result2['space_saved']} bytes")
        else:
            print("   ✗ Test failed")
        
        # Test 3: Upload different file
        print("\nTest 3: Uploading different file...")
        file3 = create_test_file("This is different content", "test3.txt")
        result3 = dedup_manager.process_file(file3, "test3.txt", user_id=1)
        
        if result3['success'] and not result3['is_duplicate']:
            print("   ✓ Different file uploaded successfully")
        else:
            print("   ✗ Test failed")
        
        # Get statistics
        print("\nDeduplication Statistics:")
        stats = dedup_manager.get_dedup_stats()
        print(f"   Total unique files: {stats['total_unique_files']}")
        print(f"   Total uploads: {stats['total_uploads']}")
        print(f"   Duplicates detected: {stats['duplicates_detected']}")
        print(f"   Space saved: {stats['space_saved_mb']:.2f} MB")
        print(f"   Deduplication ratio: {stats['deduplication_ratio']:.2f}%")
        
        print("\n" + "=" * 60)
        print("Deduplication tests completed!")
        print("=" * 60)


if __name__ == '__main__':
    Config.init_app()
    test_deduplication()
