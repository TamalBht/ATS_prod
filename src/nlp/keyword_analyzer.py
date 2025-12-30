"""
Advanced keyword analysis combining multiple NLP techniques
"""

from typing import List, Dict, Tuple, Optional
import re

from src.nlp.text_vectorizer import TextVectorizer
from src.nlp.semantic_matcher import SemanticMatcher
from src.models.resume_data import ResumeData
from src.utils.logger import get_logger


class KeywordAnalyzer:
    """Advanced keyword analysis for resumes."""
    
    def __init__(self):
        """Initialize keyword analyzer."""
        self.logger = get_logger(__name__)
        self.vectorizer = TextVectorizer()
        self.semantic_matcher = SemanticMatcher()
    
    def analyze_keywords(
        self,
        resume_data: ResumeData,
        target_keywords: List[str]
    ) -> Dict[str, any]:
        """
        Comprehensive keyword analysis.
        
        Args:
            resume_data: Parsed resume data
            target_keywords: Keywords to analyze against
            
        Returns:
            Dictionary with analysis results
        """
        text = resume_data.raw_text
        
        # TF-IDF analysis
        tfidf_keywords = self.vectorizer.extract_keywords_tfidf(text, top_n=50)
        
        # Keyword density
        density_analysis = self.vectorizer.detect_keyword_stuffing(text, target_keywords)
        
        # Direct matches
        direct_matches = self._find_direct_matches(text, target_keywords)
        
        # Semantic matches (if enabled)
        semantic_matches = {}
        if self.semantic_matcher.enabled:
            semantic_matches = self.semantic_matcher.find_similar_keywords(
                text, target_keywords
            )
        
        # Context analysis
        context_scores = self._analyze_keyword_context(text, target_keywords)
        
        # Calculate overall keyword quality
        quality_score = self._calculate_keyword_quality(
            direct_matches,
            semantic_matches,
            density_analysis,
            context_scores
        )
        
        return {
            'tfidf_keywords': tfidf_keywords[:20],  # Top 20
            'direct_matches': direct_matches,
            'semantic_matches': semantic_matches,
            'density_analysis': density_analysis,
            'context_scores': context_scores,
            'quality_score': quality_score
        }
    
    def _find_direct_matches(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, int]:
        """
        Find direct keyword matches.
        
        Args:
            text: Resume text
            keywords: Keywords to find
            
        Returns:
            Dictionary of keyword counts
        """
        text_lower = text.lower()
        matches = {}
        
        for keyword in keywords:
            # Count occurrences
            count = text_lower.count(keyword.lower())
            if count > 0:
                matches[keyword] = count
        
        return matches
    
    def _analyze_keyword_context(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, float]:
        """
        Analyze context around keywords.
        
        Keywords in action sentences ("Led Python development") score higher
        than in lists ("Skills: Python").
        
        Args:
            text: Resume text
            keywords: Keywords to analyze
            
        Returns:
            Dictionary of context scores
        """
        sentences = self._split_into_sentences(text)
        context_scores = {}
        
        # Action verbs indicate meaningful context
        action_verbs = [
            'led', 'developed', 'built', 'created', 'managed', 'designed',
            'implemented', 'architected', 'deployed', 'optimized', 'improved',
            'launched', 'delivered', 'established', 'executed'
        ]
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            total_score = 0.0
            occurrences = 0
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                if keyword_lower in sentence_lower:
                    occurrences += 1
                    
                    # Check for action verbs in same sentence
                    has_action = any(verb in sentence_lower for verb in action_verbs)
                    
                    # Check for numbers (quantifiable impact)
                    has_numbers = bool(re.search(r'\d+', sentence))
                    
                    # Calculate sentence score
                    score = 0.5  # Base score for presence
                    if has_action:
                        score += 0.3
                    if has_numbers:
                        score += 0.2
                    
                    total_score += score
            
            if occurrences > 0:
                # Average context score
                context_scores[keyword] = total_score / occurrences
        
        return context_scores
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?\n]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_keyword_quality(
        self,
        direct_matches: Dict[str, int],
        semantic_matches: Dict[str, List[Tuple[str, float]]],
        density_analysis: Dict[str, any],
        context_scores: Dict[str, float]
    ) -> float:
        """
        Calculate overall keyword quality score (0-1).
        
        Args:
            direct_matches: Direct keyword matches
            semantic_matches: Semantic matches
            density_analysis: Density analysis results
            context_scores: Context scores
            
        Returns:
            Quality score
        """
        score = 0.0
        
        # Direct match score (0-0.4)
        if direct_matches:
            match_ratio = len(direct_matches) / max(len(context_scores), 1)
            score += min(0.4, match_ratio * 0.4)
        
        # Semantic match bonus (0-0.2)
        if semantic_matches:
            semantic_ratio = len(semantic_matches) / max(len(context_scores), 1)
            score += min(0.2, semantic_ratio * 0.2)
        
        # Density score (0-0.2)
        if density_analysis['is_optimal']:
            score += 0.2
        elif not density_analysis['is_stuffed']:
            score += 0.1
        
        # Context score (0-0.2)
        if context_scores:
            avg_context = sum(context_scores.values()) / len(context_scores)
            score += min(0.2, avg_context * 0.2)
        
        return min(1.0, score)
    
    def extract_skill_phrases(
        self,
        text: str
    ) -> List[str]:
        """
        Extract skill-like phrases using NLP.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted skills
        """
        # Use TF-IDF to find important terms
        keywords = self.vectorizer.extract_keywords_tfidf(text, top_n=100)
        
        # Filter for skill-like terms (2-3 words, technical)
        skills = []
        for keyword, score in keywords:
            # Keep multi-word phrases and technical-sounding terms
            if (len(keyword.split()) >= 2 or 
                any(c.isupper() for c in keyword) or
                len(keyword) > 8):
                skills.append(keyword)
        
        return skills[:30]  # Top 30 skill candidates