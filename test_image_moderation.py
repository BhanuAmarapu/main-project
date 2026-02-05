"""
Test Image Moderation with Filename Checking
"""

from content_moderator import ContentModerator
import os

def test_image_moderation():
    moderator = ContentModerator()
    
    print("="*60)
    print("IMAGE MODERATION TEST (Filename-Based)")
    print("="*60)
    
    # Create dummy image files with different names
    test_cases = [
        ("safe_photo.jpg", True, "Safe filename"),
        ("gun.jpg", False, "Contains 'gun'"),
        ("weapon_image.png", False, "Contains 'weapon'"),
        ("nude_photo.jpg", False, "Contains 'nude'"),
        ("xxx_content.png", False, "Contains 'xxx'"),
        ("violence.jpg", False, "Contains 'violence'"),
        ("my_vacation.jpg", True, "Safe filename"),
    ]
    
    for filename, should_pass, description in test_cases:
        # Create empty file
        with open(filename, 'w') as f:
            f.write("dummy image content")
        
        result = moderator.moderate_file(filename, filename)
        
        status = "✓ PASSED" if result.is_safe else "✗ REJECTED"
        expected = "✓ PASSED" if should_pass else "✗ REJECTED"
        match = "✅" if (result.is_safe == should_pass) else "❌"
        
        print(f"\n{match} {filename}")
        print(f"   Description: {description}")
        print(f"   Expected: {expected}")
        print(f"   Got: {status}")
        
        if not result.is_safe:
            print(f"   Violation: {result.violation_type}")
            print(f"   Details: {result.violation_details}")
            print(f"   Flagged: {result.flagged_keywords}")
        
        # Cleanup
        os.remove(filename)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    test_image_moderation()
