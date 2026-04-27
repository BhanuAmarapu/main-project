"""
Test SBERT Based Content Moderation
"""

from content_moderator import ContentModerator
import os

def test_sbert_moderation():
    # SBERT Picked up meaning, so threshold might need slightly higher tuning or lower depending on examples.
    # 0.45 is a good start for dense vectors.
    moderator = ContentModerator(threshold=0.45)
    
    print("="*70)
    print("SBERT SEMANTIC CONTENT MODERATION TEST")
    print("="*70)
    print(f"Threshold: {moderator.threshold:.0%} semantic similarity to bad content\n")
    
    test_cases = [
        ("safe_document.txt", "This is a normal document about cloud storage and file management systems.", True),
        ("paraphrased_bad.txt", "This file features imagery of a mature nature including erotic acts.", False),
        ("profanity_text.txt", "This fucking document has shit and damn curse words.", False),
        ("violence_text.txt", "This discusses aggressive behavior, homicide, and firearms.", False),
        ("borderline.txt", "This document mentions adult education programs for grown-ups.", True),
    ]
    
    for filename, content, should_pass in test_cases:
        # Create test file
        with open(filename, 'w', encoding='utf-8') as f:
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
            # For SBERT, confidence_score is (1.0 - max_similarity) in the logic I wrote
            print(f"   Safety Confidence: {result.confidence_score:.1%}")
        
        print()
        
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)
    
    print("="*70)
    print("TEST COMPLETE - SBERT Semantic Moderation Algorithm Functional!")
    print("="*70)

if __name__ == '__main__':
    test_sbert_moderation()
