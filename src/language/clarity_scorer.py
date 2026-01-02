"""
Analyzes text clarity through sentence structure and language patterns.
"""

import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ClarityScorer:
    """
    Evaluates text clarity through structural analysis.
    """
    
    def __init__(self):
        """Initialize clarity scorer."""
        self.filler_words = {
            'very', 'really', 'quite', 'just', 'actually', 'basically',
            'literally', 'simply', 'somewhat', 'rather', 'pretty', 'fairly'
        }
        
        self.weak_verbs = {
            'is', 'was', 'are', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did'
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze text clarity.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with clarity metrics
        """
        if not text or len(text.strip()) < 10:
            return self._empty_result()
        
        sentences = self._split_sentences(text)
        words = self._split_words(text)
        
        if not sentences or not words:
            return self._empty_result()
        
        # Calculate metrics
        sentence_lengths = [len(self._split_words(s)) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        sentence_length_variance = self._calculate_variance(sentence_lengths)
        
        passive_voice_ratio = self._detect_passive_voice_ratio(sentences)
        filler_word_ratio = self._calculate_filler_ratio(words)
        weak_verb_ratio = self._calculate_weak_verb_ratio(words)
        
        # Sentence variety score
        variety_score = self._calculate_variety_score(sentence_length_variance)
        
        return {
            'avg_sentence_length': round(avg_sentence_length, 2),
            'sentence_length_variance': round(sentence_length_variance, 2),
            'passive_voice_ratio': round(passive_voice_ratio, 3),
            'filler_word_ratio': round(filler_word_ratio, 3),
            'weak_verb_ratio': round(weak_verb_ratio, 3),
            'variety_score': round(variety_score, 2),
            'total_sentences': len(sentences),
            'total_words': len(words)
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_words(self, text: str) -> List[str]:
        """Split text into words."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words
    
    def _calculate_variance(self, numbers: List[float]) -> float:
        """Calculate variance of a list of numbers."""
        if not numbers:
            return 0.0
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
        return variance
    
    def _detect_passive_voice_ratio(self, sentences: List[str]) -> float:
        """
        Estimate passive voice usage ratio.
        Uses heuristic: "was/were/been" + past participle
        """
        passive_indicators = r'\b(was|were|been|be|being)\s+\w+ed\b'
        passive_count = 0
        
        for sentence in sentences:
            if re.search(passive_indicators, sentence, re.IGNORECASE):
                passive_count += 1
        
        return passive_count / len(sentences) if sentences else 0.0
    
    def _calculate_filler_ratio(self, words: List[str]) -> float:
        """Calculate ratio of filler words."""
        if not words:
            return 0.0
        filler_count = sum(1 for word in words if word in self.filler_words)
        return filler_count / len(words)
    
    def _calculate_weak_verb_ratio(self, words: List[str]) -> float:
        """Calculate ratio of weak verbs."""
        if not words:
            return 0.0
        weak_verb_count = sum(1 for word in words if word in self.weak_verbs)
        return weak_verb_count / len(words)
    
    def _calculate_variety_score(self, variance: float) -> float:
        """
        Calculate sentence variety score based on length variance.
        Higher variance = better variety (to a point)
        """
        # Ideal variance is around 20-40
        if 20 <= variance <= 40:
            return 100
        elif 10 <= variance < 20 or 40 < variance <= 60:
            return 80
        elif variance < 10:
            return 60  # Too monotonous
        else:
            return 70  # Too variable
    
    def calculate_clarity_score(self, text: str) -> Dict:
        """
        Calculate overall clarity score (0-100).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with score and analysis
        """
        analysis = self.analyze(text)
        
        if analysis['total_words'] == 0:
            return {
                'score': 100.0,
                'explanation': 'Insufficient text for analysis',
                'analysis': analysis
            }
        
        # Component scores
        variety_component = analysis['variety_score'] * 0.3
        
        # Passive voice penalty (target < 20%)
        passive_penalty = max(0, (analysis['passive_voice_ratio'] - 0.20) * 100)
        passive_component = max(0, 100 - passive_penalty) * 0.3
        
        # Filler word penalty (target < 5%)
        filler_penalty = max(0, (analysis['filler_word_ratio'] - 0.05) * 200)
        filler_component = max(0, 100 - filler_penalty) * 0.2
        
        # Weak verb penalty (target < 15%)
        weak_verb_penalty = max(0, (analysis['weak_verb_ratio'] - 0.15) * 150)
        weak_verb_component = max(0, 100 - weak_verb_penalty) * 0.2
        
        total_score = (
            variety_component +
            passive_component +
            filler_component +
            weak_verb_component
        )
        
        return {
            'score': round(total_score, 2),
            'components': {
                'variety': round(variety_component, 2),
                'passive_voice': round(passive_component, 2),
                'filler_words': round(filler_component, 2),
                'weak_verbs': round(weak_verb_component, 2)
            },
            'analysis': analysis,
            'explanation': self._generate_explanation(analysis, total_score)
        }
    
    def _generate_explanation(self, analysis: Dict, score: float) -> str:
        """Generate explanation for clarity score."""
        issues = []
        
        if analysis['passive_voice_ratio'] > 0.20:
            issues.append("high passive voice usage")
        if analysis['filler_word_ratio'] > 0.05:
            issues.append("excessive filler words")
        if analysis['weak_verb_ratio'] > 0.15:
            issues.append("overuse of weak verbs")
        if analysis['variety_score'] < 70:
            issues.append("limited sentence variety")
        
        if score >= 85:
            return "Excellent clarity with strong, varied sentence structure."
        elif score >= 70:
            return f"Good clarity. Minor improvements: {', '.join(issues) if issues else 'none'}."
        elif score >= 60:
            return f"Acceptable clarity. Consider addressing: {', '.join(issues)}."
        else:
            return f"Clarity needs improvement: {', '.join(issues)}."
    
    def _empty_result(self) -> Dict:
        """Return empty result for invalid text."""
        return {
            'avg_sentence_length': 0.0,
            'sentence_length_variance': 0.0,
            'passive_voice_ratio': 0.0,
            'filler_word_ratio': 0.0,
            'weak_verb_ratio': 0.0,
            'variety_score': 100.0,
            'total_sentences': 0,
            'total_words': 0
        }