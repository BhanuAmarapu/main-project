"""
Test script for TF-IDF content similarity feature
This script tests the content similarity detection without going through the web interface
"""
import os
import sys
from content_similarity import ContentSimilarityDetector, detect_similar_content

def test_text_similarity():
    """Test basic text similarity calculation"""
    print("\n" + "="*60)
    print("TEST 1: Basic TF-IDF Similarity Calculation")
    print("="*60)
    
    detector = ContentSimilarityDetector()
    
    text1 = """
    Machine learning is a subset of artificial intelligence that focuses on 
    the development of algorithms and statistical models. These models enable 
    computer systems to improve their performance on specific tasks.
    """
    
    text2 = """
    Machine learning is a branch of artificial intelligence focused on 
    developing algorithms and statistical models. These models allow 
    computer systems to enhance their performance on particular tasks.
    """
    
    similarity = detector.compute_text_similarity(text1, text2)
    print(f"Text 1 length: {len(text1)} characters")
    print(f"Text 2 length: {len(text2)} characters")
    print(f"Similarity Score: {similarity:.2%}")
    
    if similarity >= 0.80:
        print("✓ PASS: Similarity >= 80% threshold")
    else:
        print("✗ FAIL: Similarity < 80% threshold")
    
    return similarity >= 0.80

def test_file_reading():
    """Test reading content from text files"""
    print("\n" + "="*60)
    print("TEST 2: File Content Reading")
    print("="*60)
    
    detector = ContentSimilarityDetector()
    
    # Create test files
    test_file_1 = "test_temp_1.txt"
    test_file_2 = "test_temp_2.txt"
    
    content1 = """Machine learning is transforming how we solve complex problems.
    Neural networks and deep learning are key technologies in this field.
    Applications include computer vision, natural language processing, and more."""
    
    content2 = """Machine learning is changing how we approach difficult problems.
    Neural networks and deep learning are important technologies in this area.
    Uses include computer vision, natural language understanding, and others."""
    
    try:
        # Write test files
        with open(test_file_1, 'w', encoding='utf-8') as f:
            f.write(content1)
        with open(test_file_2, 'w', encoding='utf-8') as f:
            f.write(content2)
        
        # Read files
        read_content1 = detector.read_file_content(test_file_1)
        read_content2 = detector.read_file_content(test_file_2)
        
        print(f"File 1 read successfully: {len(read_content1)} characters")
        print(f"File 2 read successfully: {len(read_content2)} characters")
        
        # Calculate similarity
        similarity = detector.compute_text_similarity(read_content1, read_content2)
        print(f"Similarity Score: {similarity:.2%}")
        
        if similarity >= 0.80:
            print("✓ PASS: File reading and similarity calculation working")
            return True
        else:
            print("✗ FAIL: Similarity below threshold")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
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
    print("TEST 3: PDF Content Reading")
    print("="*60)
    
    try:
        import PyPDF2
        print("✓ PyPDF2 module is installed")
        
        detector = ContentSimilarityDetector()
        print("✓ ContentSimilarityDetector initialized")
        
        # Check if PDF is recognized as text file
        is_pdf_supported = detector.is_text_file("test.pdf")
        print(f"PDF recognized as text file: {is_pdf_supported}")
        
        if is_pdf_supported:
            print("✓ PASS: PDF files are supported")
            return True
        else:
            print("✗ FAIL: PDF files not recognized")
            return False
            
    except ImportError:
        print("✗ FAIL: PyPDF2 not installed")
        print("  Run: pip install PyPDF2")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_schema():
    """Test if database has content_text column"""
    print("\n" + "="*60)
    print("TEST 4: Database Schema Check")
    print("="*60)
    
    try:
        import sqlite3
        conn = sqlite3.connect('db/cloud.db')
        cursor = conn.cursor()
        
        # Check uploads table schema
        cursor.execute("PRAGMA table_info(uploads)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Uploads table columns: {columns}")
        
        if 'content_text' in columns:
            print("✓ PASS: content_text column exists")
            
            # Check if any content is stored
            cursor.execute("SELECT COUNT(*) FROM uploads WHERE content_text IS NOT NULL")
            count = cursor.fetchone()[0]
            print(f"  Files with stored content: {count}")
            
            conn.close()
            return True
        else:
            print("✗ FAIL: content_text column missing")
            print("  Run: python migrate_db.py")
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TF-IDF CONTENT SIMILARITY - DIAGNOSTIC TESTS")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("TF-IDF Calculation", test_text_similarity()))
    results.append(("File Reading", test_file_reading()))
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
        print("\n🎉 All tests passed! TF-IDF feature is working correctly.")
        print("\nNext steps:")
        print("1. Restart the server: python run.py")
        print("2. Upload a text file or PDF")
        print("3. Upload a similar file (80%+ match)")
        print("4. Check if similarity is detected")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
