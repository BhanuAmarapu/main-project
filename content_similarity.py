"""
Content-Level Similarity Detection Module
Detects near-duplicate files based on content similarity (90%+ match)
even when files have different names or sizes.
"""
import os
import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from config import Config


class ContentSimilarityDetector:
    """Detect content-level similarity for files"""
    
    def __init__(self, similarity_threshold=0.60):
        """
        Initialize content similarity detector
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider files similar
        """
        self.similarity_threshold = similarity_threshold
        self.db_path = Config.DATABASE
        
        # Text file extensions to process
        self.text_extensions = {
            'txt', 'md', 'py', 'js', 'java', 'cpp', 'c', 'h', 
            'html', 'css', 'json', 'xml', 'csv', 'log', 'sql', 'pdf'
        }
    
    def is_text_file(self, filename):
        """Check if file is a text file based on extension"""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        return ext in self.text_extensions
    
    def extract_text_from_pdf(self, file_path):
        """
        Extract text content from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string, or None if error
        """
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                print(f"[DEBUG] PDF has {num_pages} pages")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                print(f"[DEBUG] Extracted {len(text)} characters from PDF")
                return text if text.strip() else None
        except Exception as e:
            print(f"[DEBUG] Error extracting text from PDF {file_path}: {e}")
            return None
    
    def read_file_content(self, file_path):
        """
        Read file content as text
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string, or None if error
        """
        # Check if it's a PDF file
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        
        # For text files, read normally
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def compute_text_similarity(self, text1, text2):
        """
        Compute similarity between two text strings using TF-IDF
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                max_features=1000  # Limit features for performance
            )
            
            # Compute TF-IDF vectors
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
    
    def find_similar_files(self, file_path, filename, current_hash):
        """
        Find files with similar content in the database
        
        Args:
            file_path: Path to uploaded file
            filename: Name of uploaded file
            current_hash: Hash of current file (to exclude exact duplicates)
            
        Returns:
            List of similar files with similarity scores
        """
        print(f"\n[DEBUG] Content Similarity Detection Started")
        print(f"[DEBUG] Checking file: {filename}")
        
        # Check if this is a text file
        if not self.is_text_file(filename):
            print(f"[DEBUG] File {filename} is NOT a text file - skipping")
            return []
        
        print(f"[DEBUG] File {filename} is a text file - proceeding")
        
        # Read content of uploaded file
        new_content = self.read_file_content(file_path)
        if not new_content:
            print(f"[DEBUG] Could not read content from {file_path}")
            return []
        
        print(f"[DEBUG] Successfully read {len(new_content)} characters from uploaded file")
        
        # Get all existing files from database with their content
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all files except exact duplicates, with their stored content
        cursor.execute("""
            SELECT f.id, f.file_name, f.file_size, f.file_hash, f.upload_timestamp, 
                   f.stored_path, 
                   (SELECT content_text FROM uploads 
                    WHERE file_id = f.id 
                    ORDER BY timestamp DESC 
                    LIMIT 1) as content_text
            FROM files f
            WHERE f.file_hash != ?
            ORDER BY f.upload_timestamp DESC
        """, (current_hash,))
        
        existing_files = cursor.fetchall()
        conn.close()
        
        print(f"[DEBUG] Found {len(existing_files)} existing files in database")

        
        similar_files = []
        files_compared = 0
        
        # Compare with each existing file
        for file_row in existing_files:
            existing_filename = file_row['file_name']
            
            # Only compare text files
            if not self.is_text_file(existing_filename):
                print(f"[DEBUG] Skipping {existing_filename} - not a text file")
                continue
            
            # Get stored content from database (not from encrypted file)
            existing_content = file_row['content_text']
            
            if not existing_content:
                print(f"[DEBUG] Skipping {existing_filename} - no content stored in database")
                continue
            
            print(f"[DEBUG] Comparing with: {existing_filename} ({len(existing_content)} chars)")
            files_compared += 1
            
            # Compute similarity
            similarity_score = self.compute_text_similarity(new_content, existing_content)
            print(f"[DEBUG] Similarity with {existing_filename}: {similarity_score:.2%}")

            
            # If similarity is above threshold, add to results
            if similarity_score >= self.similarity_threshold:
                print(f"[DEBUG] ✓ MATCH FOUND! {existing_filename} is {similarity_score:.2%} similar (threshold: {self.similarity_threshold:.0%})")
                similar_files.append({
                    'id': file_row['id'],
                    'file_name': file_row['file_name'],
                    'file_size': file_row['file_size'],
                    'file_hash': file_row['file_hash'],
                    'upload_timestamp': file_row['upload_timestamp'],
                    'stored_path': file_row['stored_path'],
                    'similarity': similarity_score
                })
        
        print(f"[DEBUG] Compared {files_compared} files, found {len(similar_files)} matches")
        
        # Sort by similarity (highest first)
        similar_files.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_files[:5]  # Return top 5 most similar


def detect_similar_content(file_path, filename, file_hash, threshold=0.60):
    """
    Main function to detect similar content
    
    Args:
        file_path: Path to uploaded file
        filename: Name of file
        file_hash: Hash of file
        threshold: Similarity threshold (default 0.60 = 60%)
        
    Returns:
        List of similar files with similarity scores
    """
    detector = ContentSimilarityDetector(similarity_threshold=threshold)
    return detector.find_similar_files(file_path, filename, file_hash)
