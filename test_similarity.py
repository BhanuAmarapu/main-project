"""
Quick test script to verify content similarity detection is working
"""
import sys
sys.path.insert(0, '.')

from content_similarity import detect_similar_content

# Test with dummy data
print("Testing content similarity detection...")
print("=" * 60)

# This will test if the module loads correctly
try:
    result = detect_similar_content(
        file_path="test.txt",  # Won't exist, but tests the import
        filename="test.txt",
        file_hash="dummy_hash",
        threshold=0.80
    )
    print("✓ Module loaded successfully")
    print(f"Result: {result}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
