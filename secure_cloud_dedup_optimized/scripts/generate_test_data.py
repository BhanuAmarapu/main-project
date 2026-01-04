"""
Generate test data for deduplication testing
"""
import os
import sys
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config


def random_string(length):
    """Generate random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_test_file(directory, filename, size_kb):
    """Create a test file"""
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w') as f:
        # Write random content
        content_size = size_kb * 1024
        f.write(random_string(content_size))
    
    return filepath


def generate_test_data():
    """Generate test data"""
    print("=" * 60)
    print("Generating Test Data")
    print("=" * 60)
    
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_files')
    
    # Small files (< 1MB)
    print("\nGenerating small files...")
    small_dir = os.path.join(base_dir, 'small')
    os.makedirs(small_dir, exist_ok=True)
    
    for i in range(10):
        create_test_file(small_dir, f'small_{i}.txt', random.randint(10, 100))
    print(f"   ✓ Created 10 small files in {small_dir}")
    
    # Medium files (1-10MB)
    print("\nGenerating medium files...")
    medium_dir = os.path.join(base_dir, 'medium')
    os.makedirs(medium_dir, exist_ok=True)
    
    for i in range(5):
        create_test_file(medium_dir, f'medium_{i}.txt', random.randint(1024, 5120))
    print(f"   ✓ Created 5 medium files in {medium_dir}")
    
    # Duplicate files
    print("\nGenerating duplicate files...")
    dup_dir = os.path.join(base_dir, 'duplicates')
    os.makedirs(dup_dir, exist_ok=True)
    
    # Create original
    original_content = random_string(50 * 1024)
    original_path = os.path.join(dup_dir, 'original.txt')
    with open(original_path, 'w') as f:
        f.write(original_content)
    
    # Create duplicates
    for i in range(5):
        dup_path = os.path.join(dup_dir, f'duplicate_{i}.txt')
        with open(dup_path, 'w') as f:
            f.write(original_content)
    
    print(f"   ✓ Created 1 original + 5 duplicates in {dup_dir}")
    
    print("\n" + "=" * 60)
    print("Test data generation completed!")
    print("=" * 60)
    print(f"\nTest files location: {base_dir}")


if __name__ == '__main__':
    generate_test_data()
