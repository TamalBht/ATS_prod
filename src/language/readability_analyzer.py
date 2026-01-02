"""
Readability metrics calculator using statistical analysis.
Implements Flesch Reading Ease and related metrics.
"""

import re
import math
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ReadabilityAnalyzer:
    """
    Calculates readability metrics for text.
    Uses established readability formulas (Flesch, Gunning Fog, etc.)
    """
    
    def __init__(self):
        """Initialize readability analyzer."""
        self.syllable_cache = {}
    
    def analyze(self, text: str) -> Dict:
        """
        Perform comprehensive readability analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with readability metrics
        """
        if not text or len(text.strip()) < 10:
            return self._empty_result()
        
        # Basic text statistics
        sentences = self._split_sentences(text)
        words = self._split_words(text)
        syllables = sum(self._count_syllables(word) for word in words)
        
        sentence_count = len(sentences)
        word_count = len(words)
        
        if sentence_count == 0 or word_count == 0:
            return self._empty_result()
        
        # Calculate metrics
        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = syllables / word_count
        
        flesch_reading_ease = self._flesch_reading_ease(
            avg_words_per_sentence, avg_syllables_per_word
        )
        flesch_kincaid_grade = self._flesch_kincaid_grade(
            avg_words_per_sentence, avg_syllables_per_word
        )
        gunning_fog = self._gunning_fog(sentences, words)
        
        return {
            'flesch_reading_ease': round(flesch_reading_ease, 2),
            'flesch_kincaid_grade': round(flesch_kincaid_grade, 2),
            'gunning_fog_index': round(gunning_fog, 2),
            'statistics': {
                'sentence_count': sentence_count,
                'word_count': word_count,
                'syllable_count': syllables,
                'avg_words_per_sentence': round(avg_words_per_sentence, 2),
                'avg_syllables_per_word': round(avg_syllables_per_word, 2)
            },
            'interpretation': self._interpret_readability(flesch_reading_ease)
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_words(self, text: str) -> List[str]:
        """Split text into words."""
        # Remove punctuation and split
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return [w for w in words if len(w) > 0]
    
    def _count_syllables(self, word: str) -> int:
        """
        Count syllables in a word using rule-based approach.
        Cached for performance.
        """
        word = word.lower()
        
        if word in self.syllable_cache:
            return self.syllable_cache[word]
        
        # Basic syllable counting rules
        count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            count -= 1
        
        # Ensure at least one syllable
        if count == 0:
            count = 1
        
        self.syllable_cache[word] = count
        return count
    
    def _flesch_reading_ease(self, avg_words_per_sentence: float, 
                            avg_syllables_per_word: float) -> float:
        """
        Calculate Flesch Reading Ease score.
        Score: 0-100 (higher = easier to read)
        Formula: 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)
        """
        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, score))  # Clamp between 0-100
    
    def _flesch_kincaid_grade(self, avg_words_per_sentence: float,
                             avg_syllables_per_word: float) -> float:
        """
        Calculate Flesch-Kincaid Grade Level.
        Returns US school grade level.
        Formula: 0.39(total words/total sentences) + 11.8(total syllables/total words) - 15.59
        """
        grade = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
        return max(0, grade)
    
    def _gunning_fog(self, sentences: List[str], words: List[str]) -> float:
        """
        Calculate Gunning Fog Index.
        Estimates years of formal education needed to understand text.
        """
        if not sentences or not words:
            return 0.0
        
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        
        avg_words_per_sentence = len(words) / len(sentences)
        percent_complex = (complex_words / len(words)) * 100
        
        fog_index = 0.4 * (avg_words_per_sentence + percent_complex)
        return max(0, fog_index)
    
    def _interpret_readability(self, flesch_score: float) -> str:
        """Provide interpretation of Flesch Reading Ease score."""
        if flesch_score >= 90:
            return "Very Easy - 5th grade level"
        elif flesch_score >= 80:
            return "Easy - 6th grade level"
        elif flesch_score >= 70:
            return "Fairly Easy - 7th grade level"
        elif flesch_score >= 60:
            return "Standard - 8th-9th grade level"
        elif flesch_score >= 50:
            return "Fairly Difficult - 10th-12th grade level"
        elif flesch_score >= 30:
            return "Difficult - College level"
        else:
            return "Very Difficult - College graduate level"
    
    def _empty_result(self) -> Dict:
        """Return empty result for invalid text."""
        return {
            'flesch_reading_ease': 0.0,
            'flesch_kincaid_grade': 0.0,
            'gunning_fog_index': 0.0,
            'statistics': {
                'sentence_count': 0,
                'word_count': 0,
                'syllable_count': 0,
                'avg_words_per_sentence': 0.0,
                'avg_syllables_per_word': 0.0
            },
            'interpretation': 'Insufficient text for analysis'
        }
    
    def calculate_readability_score(self, text: str) -> Dict:
        """
        Calculate readability score (0-100 scale).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with score and metrics
        """
        analysis = self.analyze(text)
        
        # For resumes, target Flesch score of 60-70 (standard readability)
        flesch_score = analysis['flesch_reading_ease']
        
        # Score based on deviation from ideal range
        if 60 <= flesch_score <= 70:
            score = 100
        elif 50 <= flesch_score < 60 or 70 < flesch_score <= 80:
            score = 90
        elif 40 <= flesch_score < 50 or 80 < flesch_score <= 90:
            score = 75
        elif flesch_score >= 30 or flesch_score <= 100:
            score = 60
        else:
            score = 50
        
        return {
            'score': score,
            'flesch_reading_ease': flesch_score,
            'interpretation': analysis['interpretation'],
            'metrics': analysis,
            'explanation': self._generate_explanation(flesch_score, score)
        }
    
    def _generate_explanation(self, flesch_score: float, score: int) -> str:
        """Generate explanation for readability score."""
        if score >= 90:
            return f"Excellent readability (Flesch: {flesch_score:.1f}). Clear and accessible."
        elif score >= 75:
            return f"Good readability (Flesch: {flesch_score:.1f}). Professional and clear."
        elif score >= 60:
            return f"Acceptable readability (Flesch: {flesch_score:.1f}). May benefit from simplification."
        else:
            return f"Readability needs improvement (Flesch: {flesch_score:.1f}). Consider shorter sentences."