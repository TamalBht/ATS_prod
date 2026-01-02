"""
Unit tests for Clarity Scorer (Phase 5).
"""

import unittest
from src.language.clarity_scorer import ClarityScorer


class TestClarityScorer(unittest.TestCase):
    """Test clarity scoring functionality."""
    
    def setUp(self):
        """Initialize clarity scorer for tests."""
        self.scorer = ClarityScorer()
    
    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.scorer.analyze("")
        self.assertEqual(result['total_words'], 0)
        self.assertEqual(result['total_sentences'], 0)
    
    def test_passive_voice_detection(self):
        """Test passive voice detection."""
        # Active voice
        active_text = "I developed the software. The team completed the project."
        active_result = self.scorer.analyze(active_text)
        
        # Passive voice
        passive_text = "The software was developed. The project was completed."
        passive_result = self.scorer.analyze(passive_text)
        
        self.assertGreater(
            passive_result['passive_voice_ratio'],
            active_result['passive_voice_ratio']
        )
    
    def test_filler_word_detection(self):
        """Test filler word detection."""
        clean_text = "I am skilled in Python and Java development."
        filler_text = "I am very really quite skilled in Python and Java development."
        
        clean_result = self.scorer.analyze(clean_text)
        filler_result = self.scorer.analyze(filler_text)
        
        self.assertGreater(
            filler_result['filler_word_ratio'],
            clean_result['filler_word_ratio']
        )
    
    def test_sentence_variety(self):
        """Test sentence variety scoring."""
        # Monotonous (all similar length)
        monotonous_text = "I work here. I code well. I am good."
        monotonous_result = self.scorer.analyze(monotonous_text)
        
        # Varied
        varied_text = "I work as a senior engineer. I code. I have extensive experience in backend development."
        varied_result = self.scorer.analyze(varied_text)
        
        self.assertGreater(
            varied_result['sentence_length_variance'],
            monotonous_result['sentence_length_variance']
        )
    
    def test_clarity_score_calculation(self):
        """Test overall clarity score calculation."""
        text = ("Led development of microservices architecture. "
                "Designed RESTful APIs using Python and FastAPI. "
                "Improved system performance by 40%.")
        result = self.scorer.calculate_clarity_score(text)
        
        self.assertIn('score', result)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        self.assertIn('components', result)
        self.assertIn('explanation', result)
    
    def test_weak_verb_detection(self):
        """Test weak verb detection."""
        strong_text = "Developed robust applications. Optimized database queries. Implemented caching strategy."
        weak_text = "Was responsible for applications. Had been working on queries. Have done caching."
        
        strong_result = self.scorer.analyze(strong_text)
        weak_result = self.scorer.analyze(weak_text)
        
        self.assertGreater(
            weak_result['weak_verb_ratio'],
            strong_result['weak_verb_ratio']
        )


if __name__ == '__main__':
    unittest.main()