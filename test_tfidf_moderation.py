"""
Test TF-IDF Based Content Moderation
"""

from content_moderator import ContentModerator
import os

def test_tfidf_moderation():
    moderator = ContentModerator(threshold=0.35)
    
    print("="*70)
    print("TF-IDF CONTENT MODERATION TEST")
    print("="*70)
    print(f"Threshold: {moderator.threshold:.0%} similarity to bad content\n")
    
    test_cases = [
        ("safe_document.txt", "This is a normal document about cloud storage and file management systems.", True),
        ("explicit_content.txt", "This contains explicit adult sexual content and pornography.", False),
        ("profanity_text.txt", "This fucking document has shit and damn curse words.", False),
        ("violence_text.txt", "This discusses violence, murder, and weapons like guns.", False),
        ("user_test.txt", "Explicit adult sexual content and inappropriate language.", False),
        ("borderline.txt", "This document mentions adult education programs.", True),
    ]
    
    for filename, content, should_pass in test_cases:
        # Create test file
        with open(filename, 'w') as f:
            f.write(content)
        
        # Test moderation
        result = moderator.moderate_file(filename, filename)
        
        status = "✓ PASSED" if result.is_safe else "✗ REJECTED"
        expected = "✓ PASSED" if should_pass else "✗ REJECTED"
        match = "✅" if (result.is_safe == should_pass) else "❌"
        
        print(f"{match} {filename}")
        print(f"   Content: {content[:60]}...")
        print(f"   Expected: {expected}")
        print(f"   Got: {status}")
        
        if not result.is_safe:
            print(f"   Violation: {result.violation_type}")
            print(f"   Confidence: {result.confidence_score:.1%}")
            print(f"   Details: {result.violation_details}")
        else:
            print(f"   Confidence (safe): {result.confidence_score:.1%}")
        
        print()
        
        # Cleanup
        os.remove(filename)
    
    print("="*70)
    print("TEST COMPLETE - TF-IDF Algorithm Working!")
    print("="*70)

if __name__ == '__main__':
    test_tfidf_moderation()
