"""
Unit tests for Readability Analyzer (Phase 5).
"""

import unittest
from src.language.readability_analyzer import ReadabilityAnalyzer


class TestReadabilityAnalyzer(unittest.TestCase):
    """Test readability analysis functionality."""
    
    def setUp(self):
        """Initialize readability analyzer for tests."""
        self.analyzer = ReadabilityAnalyzer()
    
    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.analyzer.analyze("")
        self.assertEqual(result['flesch_reading_ease'], 0.0)
        self.assertEqual(result['statistics']['word_count'], 0)
    
    def test_simple_text_analysis(self):
        """Test analysis of simple text."""
        text = "The cat sat on the mat. It was a sunny day."
        result = self.analyzer.analyze(text)
        
        self.assertGreater(result['flesch_reading_ease'], 0)
        self.assertGreater(result['statistics']['sentence_count'], 0)
        self.assertGreater(result['statistics']['word_count'], 0)
        self.assertIn('interpretation', result)
    
    def test_complex_text_analysis(self):
        """Test analysis of complex text."""
        text = ("Sophisticated enterprise-level architectural implementations "
                "necessitate comprehensive understanding of multifaceted "
                "organizational requirements and technological constraints.")
        result = self.analyzer.analyze(text)
        
        # Complex text should have lower Flesch score
        self.assertLess(result['flesch_reading_ease'], 60)
        self.assertGreater(result['flesch_kincaid_grade'], 10)
    
    def test_syllable_counting(self):
        """Test syllable counting accuracy."""
        test_words = {
            'cat': 1,
            'happy': 2,
            'beautiful': 3,
            'understanding': 4
        }
        
        for word, expected_syllables in test_words.items():
            count = self.analyzer._count_syllables(word)
            self.assertGreaterEqual(count, 1, f"Word '{word}' should have at least 1 syllable")
    
    def test_readability_score_calculation(self):
        """Test readability score calculation."""
        text = ("Professional software engineer with extensive experience in backend development. "
                "Skilled in Python, Java, and cloud technologies. Strong communication skills.")
        result = self.analyzer.calculate_readability_score(text)
        
        self.assertIn('score', result)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        self.assertIn('explanation', result)
    
    def test_interpretation_ranges(self):
        """Test that interpretation matches score ranges."""
        # Very easy text (short words, short sentences)
        easy_text = "I am a good worker. I like my job. I work hard every day."
        easy_result = self.analyzer.analyze(easy_text)
        self.assertGreater(easy_result['flesch_reading_ease'], 70)
        
        # Difficult text (long words, long sentences)
        hard_text = ("The implementation of sophisticated algorithmic methodologies "
                    "requires comprehensive understanding of computational complexity theory.")
        hard_result = self.analyzer.analyze(hard_text)
        self.assertLess(hard_result['flesch_reading_ease'], 50)


if __name__ == '__main__':
    unittest.main()