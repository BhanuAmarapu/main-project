"""
Test to show image filename detection
"""

from content_moderator import ContentModerator
import os

moderator = ContentModerator()

print("="*60)
print("IMAGE FILENAME MODERATION TEST")
print("="*60)

# Test different filenames
test_files = [
    "gun.jpg",
    "weapon.png", 
    "photo.jpg",
    "IMG_1234.jpg",
    "my_gun_collection.jpg",
    "violence.png"
]

for filename in test_files:
    # Create dummy file
    with open(filename, 'w') as f:
        f.write("dummy")
    
    result = moderator.moderate_file(filename, filename)
    
    status = "✓ ALLOWED" if result.is_safe else "✗ REJECTED"
    print(f"\n{filename}: {status}")
    
    if not result.is_safe:
        print(f"  Reason: {result.violation_details}")
    
    os.remove(filename)

print("\n" + "="*60)
print("IMPORTANT: This only checks FILENAMES, not image content!")
print("="*60)
