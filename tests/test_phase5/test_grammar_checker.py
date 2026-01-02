"""
Unit tests for Grammar Checker (Phase 5).
"""

import unittest
from src.language.grammar_checker import GrammarChecker


class TestGrammarChecker(unittest.TestCase):
    """Test grammar checking functionality."""
    
    def setUp(self):
        """Initialize grammar checker for tests."""
        # Use basic rules for consistent testing
        self.checker = GrammarChecker(use_language_tool=False)
    
    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.checker.check_text("")
        self.assertEqual(result['total_issues'], 0)
        self.assertEqual(result['method'], 'none')
    
    def test_basic_check(self):
        """Test basic grammar checking."""
        text = "This is a simple sentence with  double spaces."
        result = self.checker.check_text(text)
        
        self.assertGreater(result['total_issues'], 0)
        self.assertIn('method', result)
        self.assertIn('issue_types', result)
    
    def test_grammar_score_perfect_text(self):
        """Test grammar score for perfect text."""
        text = "This is a well-written professional summary with no errors."
        result = self.checker.calculate_grammar_score(text)
        
        self.assertIn('score', result)
        self.assertGreaterEqual(result['score'], 90)
        self.assertIn('explanation', result)
    
    def test_grammar_score_with_issues(self):
        """Test grammar score with multiple issues."""
        text = "This  text  has  multiple  double  spaces everywhere."
        result = self.checker.calculate_grammar_score(text)
        
        self.assertIn('score', result)
        self.assertLess(result['score'], 100)
        self.assertGreater(result['total_issues'], 0)
    
    def test_short_text_handling(self):
        """Test handling of very short text."""
        text = "Hi there"
        result = self.checker.calculate_grammar_score(text)
        
        self.assertEqual(result['score'], 100.0)
        self.assertIn('too short', result['explanation'].lower())
    
    def test_score_bounds(self):
        """Test that scores stay within 50-100 range."""
        # Text with many issues
        text = "this  text  has  many  issues  " * 50
        result = self.checker.calculate_grammar_score(text)
        
        self.assertGreaterEqual(result['score'], 50)
        self.assertLessEqual(result['score'], 100)


if __name__ == '__main__':
    unittest.main()