"""
Test script for SBERT semantic content similarity feature
This script tests the semantic similarity detection without going through the web interface
"""
import os
import sys
from content_similarity import ContentSimilarityDetector, detect_similar_content

def test_text_similarity():
    """Test basic semantic similarity calculation"""
    print("\n" + "="*60)
    print("TEST 1: SBERT Semantic Similarity Calculation")
    print("="*60)
    
    detector = ContentSimilarityDetector()
    
    # These texts mean the same but use different words (SBERT should pass, TF-IDF might struggle)
    text1 = """
    Artificial Intelligence is rapidly evolving and changing the global workforce.
    Many industries are adopting automated systems to improve productivity.
    """
    
    text2 = """
    AI is progressing fast and transforming the employment landscape worldwide.
    Various sectors are implementing robotics to enhance efficiency.
    """
    
    similarity = detector.compute_text_similarity(text1, text2)
    print(f"Text 1: '{text1.strip()[:60]}...'")
    print(f"Text 2: '{text2.strip()[:60]}...'")
    print(f"Semantic Similarity Score: {similarity:.2%}")
    
    if similarity >= 0.70: # SBERT picks up meaning better, usually lower than 1.0 but high enough
        print("✓ PASS: High semantic similarity detected")
    else:
        print("✗ FAIL: Similarity below expected semantic threshold")
    
    return similarity >= 0.70

def test_file_reading():
    """Test reading content from text files"""
    print("\n" + "="*60)
    print("TEST 2: File Content Reading and Semantic Check")
    print("="*60)
    
    detector = ContentSimilarityDetector()
    
    # Create test files
    test_file_1 = "test_temp_1.txt"
    test_file_2 = "test_temp_2.txt"
    
    content1 = "The weather is lovely today in London."
    content2 = "It is a beautiful sunny day in the UK capital."
    
    try:
        # Write test files
        with open(test_file_1, 'w', encoding='utf-8') as f:
            f.write(content1)
        with open(test_file_2, 'w', encoding='utf-8') as f:
            f.write(content2)
        
        # Read files
        read_content1 = detector.read_file_content(test_file_1)
        read_content2 = detector.read_file_content(test_file_2)
        
        print(f"File 1 content: {read_content1}")
        print(f"File 2 content: {read_content2}")
        
        # Calculate similarity
        similarity = detector.compute_text_similarity(read_content1, read_content2)
        print(f"Semantic Similarity Score: {similarity:.2%}")
        
        if similarity >= 0.60:
            print("✓ PASS: Semantic similarity detected between paraphrases")
            return True
        else:
            print("✗ FAIL: Paraphrase similarity too low")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file_1):
            os.remove(test_file_1)
        if os.path.exists(test_file_2):
            os.remove(test_file_2)

def test_pdf_reading():
    """Test reading content from PDF files"""
    print("\n" + "="*60)
    print("TEST 3: PDF Content Reading Support")
    print("="*60)
    
    detector = ContentSimilarityDetector()
    is_pdf_supported = detector.is_text_file("test.pdf")
    print(f"PDF recognized as text-capable file: {is_pdf_supported}")
    
    if is_pdf_supported:
        print("✓ PASS: PDF files are supported")
        return True
    else:
        print("✗ FAIL: PDF files not recognized")
        return False

def test_database_schema():
    """Test if database has content_text column"""
    print("\n" + "="*60)
    print("TEST 4: Database Requirement Check")
    print("="*60)
    
    try:
        from mysql_wrapper import get_mysql_connection
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        # Check uploads table schema for MySQL
        cursor.execute("DESCRIBE uploads")
        columns = [row['Field'] for row in cursor.fetchall()]
        
        print(f"Uploads table columns: {columns}")
        
        if 'content_text' in columns:
            print("✓ PASS: content_text column exists in MySQL")
            conn.close()
            return True
        else:
            print("✗ FAIL: content_text column missing")
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SBERT SEMANTIC CONTENT SIMILARITY - DIAGNOSTIC TESTS")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("SBERT Calculation", test_text_similarity()))
    results.append(("Paraphrase Detection", test_file_reading()))
    results.append(("PDF Support", test_pdf_reading()))
    results.append(("Database Schema", test_database_schema()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! SBERT semantic feature is working correctly.")
        print("\nNext steps:")
        print("1. Restart the server: python run.py")
        print("2. Upload a text file or PDF")
        print("3. Upload a semantically similar file")
        print("4. Check if similarity is detected")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
