"""
Semantic similarity matching (optional spaCy integration)
"""

from typing import List, Dict, Tuple, Optional
import re

from src.config.settings import get_settings
from src.utils.logger import get_logger

# Try to import spaCy (optional)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class SemanticMatcher:
    """Matches keywords using semantic similarity."""
    
    def __init__(self):
        """Initialize semantic matcher."""
        self.logger = get_logger(__name__)
        self.settings = get_settings()
        self.config = self.settings.get('nlp', {}).get('semantic', {})
        
        self.nlp = None
        self.enabled = self.config.get('enabled', False) and SPACY_AVAILABLE
        
        if self.enabled:
            self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model."""
        if not SPACY_AVAILABLE:
            self.logger.warning("spaCy not available. Semantic matching disabled.")
            self.enabled = False
            return
        
        model_name = self.config.get('model', 'en_core_web_sm')
        
        try:
            self.nlp = spacy.load(model_name)
            self.logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            self.logger.warning(
                f"spaCy model '{model_name}' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            self.enabled = False
    
    def calculate_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not self.enabled or not self.nlp:
            # Fallback: simple word overlap
            return self._simple_similarity(text1, text2)
        
        try:
            doc1 = self.nlp(text1.lower())
            doc2 = self.nlp(text2.lower())
            
            return doc1.similarity(doc2)
            
        except Exception as e:
            self.logger.warning(f"Similarity calculation failed: {e}")
            return self._simple_similarity(text1, text2)
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """
        Simple word overlap similarity (fallback).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_similar_keywords(
        self,
        resume_text: str,
        target_keywords: List[str],
        threshold: Optional[float] = None
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Find keywords in resume similar to target keywords.
        
        Args:
            resume_text: Resume text
            target_keywords: Keywords to match
            threshold: Similarity threshold (uses config default if None)
            
        Returns:
            Dict mapping target keywords to list of (matched_word, similarity)
        """
        if threshold is None:
            threshold = self.config.get('similarity_threshold', 0.6)
        
        # Extract words/phrases from resume
        resume_words = self._extract_meaningful_words(resume_text)
        
        matches = {}
        
        for target_kw in target_keywords:
            similar_words = []
            
            for resume_word in resume_words:
                similarity = self.calculate_similarity(target_kw, resume_word)
                
                if similarity >= threshold:
                    similar_words.append((resume_word, similarity))
            
            # Sort by similarity
            similar_words.sort(key=lambda x: x[1], reverse=True)
            
            if similar_words:
                matches[target_kw] = similar_words[:5]  # Top 5 matches
        
        return matches
    
    def _extract_meaningful_words(self, text: str) -> List[str]:
        """
        Extract meaningful words/phrases from text.
        
        Args:
            text: Input text
            
        Returns:
            List of words/phrases
        """
        # Simple extraction: words longer than 3 characters
        words = text.lower().split()
        meaningful = [w for w in words if len(w) > 3]
        
        # Also extract bigrams
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) > 8:  # Meaningful bigrams
                bigrams.append(bigram)
        
        return meaningful + bigrams
    
    def match_skill_variants(
        self,
        skill: str,
        skill_list: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Match a skill against list of skills, finding similar ones.
        
        Args:
            skill: Target skill
            skill_list: List of skills to match against
            
        Returns:
            List of (matched_skill, similarity) tuples
        """
        matches = []
        
        for candidate_skill in skill_list:
            similarity = self.calculate_similarity(skill, candidate_skill)
            
            if similarity > 0.5:  # Lower threshold for skill matching
                matches.append((candidate_skill, similarity))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches