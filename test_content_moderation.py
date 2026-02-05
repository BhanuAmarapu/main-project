"""
Test Content Moderation System

This script tests the content moderator with various types of content.
"""

from content_moderator import ContentModerator
import os

def test_moderation():
    moderator = ContentModerator()
    
    print("="*60)
    print("CONTENT MODERATION TEST")
    print("="*60)
    
    # Test 1: Safe content
    print("\n[TEST 1] Safe Content")
    with open('test_safe.txt', 'w') as f:
        f.write("This is a normal document about cloud storage and file management.")
    
    result = moderator.moderate_file('test_safe.txt', 'test_safe.txt')
    print(f"Result: {'✓ PASSED' if result.is_safe else '✗ REJECTED'}")
    if not result.is_safe:
        print(f"Violation: {result.violation_type}")
        print(f"Details: {result.violation_details}")
    os.remove('test_safe.txt')
    
    # Test 2: Explicit content
    print("\n[TEST 2] Explicit Content")
    with open('test_explicit.txt', 'w') as f:
        f.write("This contains explicit adult sexual content.")
    
    result = moderator.moderate_file('test_explicit.txt', 'test_explicit.txt')
    print(f"Result: {'✓ PASSED' if result.is_safe else '✗ REJECTED'}")
    if not result.is_safe:
        print(f"Violation: {result.violation_type}")
        print(f"Details: {result.violation_details}")
        print(f"Flagged keywords: {result.flagged_keywords}")
    os.remove('test_explicit.txt')
    
    # Test 3: Profanity
    print("\n[TEST 3] Profanity")
    with open('test_profanity.txt', 'w') as f:
        f.write("This is a damn test with some shit in it.")
    
    result = moderator.moderate_file('test_profanity.txt', 'test_profanity.txt')
    print(f"Result: {'✓ PASSED' if result.is_safe else '✗ REJECTED'}")
    if not result.is_safe:
        print(f"Violation: {result.violation_type}")
        print(f"Details: {result.violation_details}")
        print(f"Flagged keywords: {result.flagged_keywords}")
    os.remove('test_profanity.txt')
    
    # Test 4: Violence
    print("\n[TEST 4] Violence")
    with open('test_violence.txt', 'w') as f:
        f.write("This document discusses violence and weapons.")
    
    result = moderator.moderate_file('test_violence.txt', 'test_violence.txt')
    print(f"Result: {'✓ PASSED' if result.is_safe else '✗ REJECTED'}")
    if not result.is_safe:
        print(f"Violation: {result.violation_type}")
        print(f"Details: {result.violation_details}")
        print(f"Flagged keywords: {result.flagged_keywords}")
    os.remove('test_violence.txt')
    
    # Test 5: Your example
    print("\n[TEST 5] Your Test Case")
    with open('test_user_example.txt', 'w') as f:
        f.write("""This is a moderation test file.

The following line intentionally contains explicit adult content for
testing purposes:

"Explicit adult sexual content and inappropriate language."

This file is used to verify that the AI moderation system correctly
rejects unsafe uploads.""")
    
    result = moderator.moderate_file('test_user_example.txt', 'test_user_example.txt')
    print(f"Result: {'✓ PASSED' if result.is_safe else '✗ REJECTED'}")
    if not result.is_safe:
        print(f"Violation: {result.violation_type}")
        print(f"Details: {result.violation_details}")
        print(f"Confidence: {result.confidence_score:.1%}")
        print(f"Flagged keywords: {result.flagged_keywords}")
    os.remove('test_user_example.txt')
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    test_moderation()
