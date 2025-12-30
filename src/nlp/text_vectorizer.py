"""
Text vectorization using TF-IDF
"""

from typing import List, Dict, Tuple, Optional
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from src.config.settings import get_settings
from src.utils.logger import get_logger


class TextVectorizer:
    """Vectorizes text using TF-IDF for keyword analysis."""
    
    def __init__(self):
        """Initialize text vectorizer."""
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.config = self.settings.get('nlp', {}).get('tfidf', {})
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.config.get('max_features', 500),
            ngram_range=tuple(self.config.get('ngram_range', [1, 3])),
            min_df=self.config.get('min_df', 1),
            max_df=self.config.get('max_df', 0.95),
            lowercase=True,
            stop_words='english'
        )
        
        self.fitted = False
    
    def extract_keywords_tfidf(
        self,
        text: str,
        top_n: int = 50
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples sorted by score
        """
        if not text or len(text.strip()) < 10:
            return []
        
        try:
            # For short texts, adjust parameters
            min_df = 1
            max_df = 1.0  # Allow all terms for single document
            
            # Create vectorizer for single document
            vectorizer = TfidfVectorizer(
                max_features=self.config.get('max_features', 500),
                ngram_range=tuple(self.config.get('ngram_range', [1, 3])),
                min_df=min_df,
                max_df=max_df,
                lowercase=True,
                stop_words='english'
            )
            
            # Fit and transform on single document
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores for the document
            scores = tfidf_matrix.toarray()[0]
            
            # Create keyword-score pairs
            keyword_scores = list(zip(feature_names, scores))
            
            # Filter out zero scores and sort
            keyword_scores = [(kw, score) for kw, score in keyword_scores if score > 0]
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_n]
            
        except Exception as e:
            self.logger.error(f"TF-IDF extraction failed: {e}")
            return []
    
    def calculate_keyword_density(
        self,
        text: str,
        keywords: List[str]
    ) -> float:
        """
        Calculate keyword density (keywords per 100 words).
        
        Args:
            text: Input text
            keywords: List of keywords to check
            
        Returns:
            Density score
        """
        if not text or not keywords:
            return 0.0
        
        # Count total words
        words = text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        # Count keyword occurrences (whole word matches only)
        text_lower = ' ' + text.lower() + ' '  # Add spaces for boundary matching
        keyword_count = 0
        
        for kw in keywords:
            kw_lower = kw.lower()
            # Count occurrences as whole words
            import re
            pattern = r'\b' + re.escape(kw_lower) + r'\b'
            matches = re.findall(pattern, text_lower)
            keyword_count += len(matches)
        
        # Calculate density (per 100 words)
        density = (keyword_count / total_words) * 100
        
        return density
    
    def detect_keyword_stuffing(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, any]:
        """
        Detect keyword stuffing.
        
        Args:
            text: Input text
            keywords: List of keywords
            
        Returns:
            Dictionary with stuffing analysis
        """
        density = self.calculate_keyword_density(text, keywords)
        
        max_density = self.settings.get('nlp', {}).get('keyword_quality', {}).get('max_density', 20.0)
        optimal_density = self.settings.get('nlp', {}).get('keyword_quality', {}).get('optimal_density', 10.0)
        
        is_stuffed = density > max_density
        is_optimal = abs(density - optimal_density) < 0.5
        
        return {
            'density': density,
            'is_stuffed': is_stuffed,
            'is_optimal': is_optimal,
            'max_allowed': max_density,
            'optimal_range': (optimal_density - 0.5, optimal_density + 0.5)
        }
    
    def extract_ngrams(
        self,
        text: str,
        n_range: Tuple[int, int] = (2, 3)
    ) -> List[str]:
        """
        Extract n-grams from text.
        
        Args:
            text: Input text
            n_range: Range of n-gram sizes (min, max)
            
        Returns:
            List of n-grams
        """
        words = text.lower().split()
        ngrams = []
        
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                # Filter out stopwords-only ngrams
                if len(ngram) > 3:  # Minimum length
                    ngrams.append(ngram)
        
        return ngrams
    
    def calculate_term_frequency(
        self,
        text: str,
        terms: List[str]
    ) -> Dict[str, int]:
        """
        Calculate frequency of terms in text.
        
        Args:
            text: Input text
            terms: List of terms to count
            
        Returns:
            Dictionary of term frequencies
        """
        text_lower = text.lower()
        frequencies = {}
        
        for term in terms:
            term_lower = term.lower()
            count = text_lower.count(term_lower)
            if count > 0:
                frequencies[term] = count
        
        return frequencies
    
    def score_keyword_relevance(
        self,
        resume_text: str,
        role_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Score relevance of role keywords in resume.
        
        Args:
            resume_text: Resume text
            role_keywords: Keywords for target role
            
        Returns:
            Dictionary mapping keywords to relevance scores
        """
        # Extract TF-IDF keywords from resume
        resume_keywords = self.extract_keywords_tfidf(resume_text, top_n=100)
        resume_keyword_dict = {kw: score for kw, score in resume_keywords}
        
        # Score each role keyword
        relevance_scores = {}
        
        for role_kw in role_keywords:
            role_kw_lower = role_kw.lower()
            
            # Direct match
            if role_kw_lower in resume_keyword_dict:
                relevance_scores[role_kw] = resume_keyword_dict[role_kw_lower]
            else:
                # Check for partial matches
                max_score = 0.0
                for resume_kw, score in resume_keywords:
                    if role_kw_lower in resume_kw or resume_kw in role_kw_lower:
                        max_score = max(max_score, score * 0.8)  # Partial match penalty
                
                relevance_scores[role_kw] = max_score
        
        return relevance_scores