"""
AI Content Moderation Module - Enhanced with TF-IDF

Provides intelligent content moderation using TF-IDF algorithm for:
- Text content filtering (profanity, explicit content, violence)
- Image filename checking
- Video moderation (placeholder)

Uses TF-IDF similarity scoring against known bad content patterns.
"""

import os
import re
from dataclasses import dataclass
from typing import Tuple, List, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@dataclass
class ModerationResult:
    """Result of content moderation check"""
    is_safe: bool
    violation_type: Optional[str] = None
    violation_details: Optional[str] = None
    confidence_score: float = 0.0
    flagged_keywords: List[str] = None
    
    def __post_init__(self):
        if self.flagged_keywords is None:
            self.flagged_keywords = []


class ContentModerator:
    """
    Intelligent content moderation service using TF-IDF
    
    Analyzes text content using TF-IDF similarity against known bad content patterns.
    """
    
    def __init__(self, strict_mode=False, threshold=0.35):
        """
        Initialize content moderator with TF-IDF
        
        Args:
            strict_mode: If True, uses stricter filtering rules
            threshold: TF-IDF similarity threshold (0.35 = 35% similarity to bad content)
        """
        self.strict_mode = strict_mode
        self.threshold = threshold
        
        # Training data: Examples of bad content for each category
        self.explicit_examples = [
            "explicit adult sexual content pornography",
            "nude naked nsfw erotic sex xxx porn",
            "sexual explicit adult content inappropriate",
            "pornographic material adult entertainment",
            "explicit sexual imagery nude photos"
        ]
        
        self.profanity_examples = [
            "fuck shit damn bitch ass bastard",
            "fucking hell piss cock dick pussy",
            "goddamn motherfucker asshole crap",
            "bullshit fucking damn hell shit",
            "curse words profanity vulgar language"
        ]
        
        self.violence_examples = [
            "kill murder violence weapon gun",
            "torture abuse rape violent attack",
            "terrorism bomb explosive weapon",
            "gore blood violent death murder",
            "hate crime racist violence abuse"
        ]
        
        # Initialize TF-IDF vectorizers for each category
        self.explicit_vectorizer = TfidfVectorizer()
        self.profanity_vectorizer = TfidfVectorizer()
        self.violence_vectorizer = TfidfVectorizer()
        
        # Fit vectorizers with training data
        self.explicit_vectors = self.explicit_vectorizer.fit_transform(self.explicit_examples)
        self.profanity_vectors = self.profanity_vectorizer.fit_transform(self.profanity_examples)
        self.violence_vectors = self.violence_vectorizer.fit_transform(self.violence_examples)
        
    def analyze_text_with_tfidf(self, text: str) -> Tuple[str, float, List[str]]:
        """
        Analyze text using TF-IDF similarity against bad content patterns
        
        Args:
            text: Text content to analyze
            
        Returns:
            Tuple of (violation_type, confidence_score, flagged_keywords)
        """
        text_lower = text.lower()
        
        # Calculate similarity scores for each category
        try:
            # Explicit content check
            text_vector_explicit = self.explicit_vectorizer.transform([text_lower])
            explicit_similarities = cosine_similarity(text_vector_explicit, self.explicit_vectors)
            max_explicit_score = np.max(explicit_similarities)
            
            # Profanity check
            text_vector_profanity = self.profanity_vectorizer.transform([text_lower])
            profanity_similarities = cosine_similarity(text_vector_profanity, self.profanity_vectors)
            max_profanity_score = np.max(profanity_similarities)
            
            # Violence check
            text_vector_violence = self.violence_vectorizer.transform([text_lower])
            violence_similarities = cosine_similarity(text_vector_violence, self.violence_vectors)
            max_violence_score = np.max(violence_similarities)
            
            # Determine which category has highest score
            scores = {
                'EXPLICIT': max_explicit_score,
                'PROFANITY': max_profanity_score,
                'VIOLENCE': max_violence_score
            }
            
            violation_type = max(scores, key=scores.get)
            confidence = scores[violation_type]
            
            # Extract flagged keywords based on category
            flagged_keywords = []
            if violation_type == 'EXPLICIT':
                keywords = {'explicit', 'adult', 'sexual', 'porn', 'xxx', 'nude', 'naked', 'nsfw', 'sex', 'erotic'}
            elif violation_type == 'PROFANITY':
                keywords = {'fuck', 'shit', 'damn', 'bitch', 'ass', 'bastard', 'hell', 'piss', 'cock', 'dick', 'pussy'}
            elif violation_type == 'VIOLENCE':
                keywords = {'kill', 'murder', 'rape', 'torture', 'abuse', 'violence', 'weapon', 'gun', 'bomb', 'hate'}
            
            for keyword in keywords:
                if keyword in text_lower:
                    flagged_keywords.append(keyword)
            
            return violation_type, confidence, flagged_keywords
            
        except Exception as e:
            print(f"[MODERATION] TF-IDF analysis error: {e}")
            return None, 0.0, []
    
    def moderate_text(self, file_path: str) -> ModerationResult:
        """
        Moderate text file content using TF-IDF
        
        Args:
            file_path: Path to text file
            
        Returns:
            ModerationResult with safety status and details
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return ModerationResult(is_safe=True, confidence_score=1.0)
            
            # Analyze with TF-IDF
            violation_type, confidence, flagged_keywords = self.analyze_text_with_tfidf(content)
            
            # Check if confidence exceeds threshold
            if confidence >= self.threshold:
                violation_details = f"TF-IDF analysis detected {violation_type.lower()} content (similarity: {confidence:.1%})"
                if flagged_keywords:
                    violation_details += f". Found keywords: {', '.join(flagged_keywords[:5])}"
                
                return ModerationResult(
                    is_safe=False,
                    violation_type=violation_type,
                    violation_details=violation_details,
                    confidence_score=confidence,
                    flagged_keywords=flagged_keywords
                )
            
            return ModerationResult(is_safe=True, confidence_score=1.0 - confidence)
            
        except Exception as e:
            print(f"[MODERATION] Error reading text file: {e}")
            # On error, allow upload but log it
            return ModerationResult(
                is_safe=True,
                violation_details=f"Error during moderation: {str(e)}"
            )
    
    def moderate_image(self, file_path: str) -> ModerationResult:
        """
        Moderate image content (filename-based checking)
        
        Args:
            file_path: Path to image file
            
        Returns:
            ModerationResult with safety status
        """
        try:
            # Get filename for keyword checking
            filename = os.path.basename(file_path).lower()
            
            # Check filename for suspicious keywords
            suspicious_image_keywords = {
                'gun', 'weapon', 'nude', 'naked', 'porn', 'xxx', 'sex',
                'explicit', 'nsfw', 'violence', 'blood', 'gore', 'kill',
                'murder', 'rape', 'abuse', 'hate', 'racist', 'terrorist'
            }
            
            flagged_keywords = []
            for keyword in suspicious_image_keywords:
                if keyword in filename:
                    flagged_keywords.append(keyword)
            
            if flagged_keywords:
                return ModerationResult(
                    is_safe=False,
                    violation_type='EXPLICIT' if any(k in ['nude', 'naked', 'porn', 'xxx', 'sex', 'nsfw'] for k in flagged_keywords) else 'VIOLENCE',
                    violation_details=f"Suspicious filename detected: {', '.join(flagged_keywords)}",
                    confidence_score=0.7,
                    flagged_keywords=flagged_keywords
                )
            
            # If no suspicious keywords in filename, allow
            return ModerationResult(
                is_safe=True,
                violation_details="Filename check passed",
                confidence_score=0.5
            )
            
        except Exception as e:
            print(f"[MODERATION] Error checking image: {e}")
            return ModerationResult(
                is_safe=True,
                violation_details=f"Error during moderation: {str(e)}"
            )
    
    def moderate_video(self, file_path: str) -> ModerationResult:
        """
        Moderate video content (placeholder)
        
        Args:
            file_path: Path to video file
            
        Returns:
            ModerationResult with safety status
        """
        try:
            # Placeholder for video moderation
            return ModerationResult(
                is_safe=True,
                violation_details="Video moderation not yet implemented",
                confidence_score=0.5
            )
            
        except Exception as e:
            print(f"[MODERATION] Error checking video: {e}")
            return ModerationResult(is_safe=True)
    
    def moderate_file(self, file_path: str, filename: str) -> ModerationResult:
        """
        Moderate any file based on its type using TF-IDF
        
        Args:
            file_path: Path to file
            filename: Name of file (used to determine type)
            
        Returns:
            ModerationResult with safety status
        """
        # Determine file type from extension
        ext = os.path.splitext(filename)[1].lower()
        
        # Text files
        text_extensions = {'.txt', '.md', '.log', '.csv', '.json', '.xml', 
                          '.py', '.js', '.html', '.css', '.java', '.cpp', 
                          '.c', '.h', '.sql', '.sh'}
        
        # Image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
                           '.svg', '.ico', '.tiff'}
        
        # Video files
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', 
                           '.webm', '.m4v'}
        
        # Route to appropriate moderator
        if ext in text_extensions:
            return self.moderate_text(file_path)
        elif ext in image_extensions:
            return self.moderate_image(file_path)
        elif ext in video_extensions:
            return self.moderate_video(file_path)
        else:
            # Unknown file type - allow but log
            return ModerationResult(
                is_safe=True,
                violation_details=f"Unknown file type: {ext}"
            )


if __name__ == '__main__':
    # Quick test
    moderator = ContentModerator()
    
    # Test with bad content
    with open('test_bad.txt', 'w') as f:
        f.write("This contains explicit adult sexual content.")
    
    result = moderator.moderate_file('test_bad.txt', 'test_bad.txt')
    print(f"Result: {'SAFE' if result.is_safe else 'REJECTED'}")
    if not result.is_safe:
        print(f"Violation: {result.violation_type}")
        print(f"Confidence: {result.confidence_score:.1%}")
        print(f"Details: {result.violation_details}")
    
    os.remove('test_bad.txt')
