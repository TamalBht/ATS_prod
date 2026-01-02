"""
Unit tests for Language Scorer (Phase 5).
"""

import unittest
from src.language.language_scorer import LanguageScorer


class TestLanguageScorer(unittest.TestCase):
    """Test integrated language scoring functionality."""
    
    def setUp(self):
        """Initialize language scorer for tests."""
        self.scorer = LanguageScorer(use_language_tool=False)
    
    def test_score_text_basic(self):
        """Test basic text scoring."""
        text = "Experienced software engineer with strong Python skills."
        result = self.scorer.score_text(text, "summary")
        
        self.assertIn('language_quality_score', result)
        self.assertIn('components', result)
        self.assertIn('grammar', result['components'])
        self.assertIn('readability', result['components'])
        self.assertIn('clarity', result['components'])
        self.assertIn('recommendations', result)
    
    def test_score_empty_text(self):
        """Test scoring of empty text."""
        result = self.scorer.score_text("", "summary")
        
        self.assertEqual(result['language_quality_score'], 100.0)
        self.assertIn('Insufficient text', result['overall_assessment'])
    
    def test_score_resume_sections(self):
        """Test scoring complete resume sections."""
        parsed_resume = {
            'summary': 'Experienced engineer with Python expertise.',
            'experience': [
                {
                    'title': 'Senior Engineer',
                    'description': 'Developed scalable microservices.'
                }
            ],
            'skills': ['Python', 'AWS'],
            'education': [
                {
                    'degree': 'BS Computer Science',
                    'institution': 'University XYZ'
                }
            ]
        }
        
        result = self.scorer.score_resume_sections(parsed_resume)
        
        self.assertIn('overall_language_score', result)
        self.assertIn('section_scores', result)
        self.assertIn('global_analysis', result)
        self.assertIn('summary', result)
        self.assertGreaterEqual(result['overall_language_score'], 0)
        self.assertLessEqual(result['overall_language_score'], 100)
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated appropriately."""
        # Text with issues
        poor_text = ("The system was built by me. "
                    "The code was really very written. "
                    "Performance was just achieved basically.")
        
        result = self.scorer.score_text(poor_text, "test")
        
        self.assertGreater(len(result['recommendations']), 0)
        self.assertTrue(any(
            rec['category'] in ['grammar', 'readability', 'clarity']
            for rec in result['recommendations']
        ))
    
    def test_section_text_extraction(self):
        """Test extraction of text from various section formats."""
        # String format
        text1 = self.scorer._extract_section_text("Simple string text")
        self.assertEqual(text1, "Simple string text")
        
        # List format
        text2 = self.scorer._extract_section_text(["Item 1", "Item 2"])
        self.assertIn("Item 1", text2)
        self.assertIn("Item 2", text2)
        
        # Dict format
        text3 = self.scorer._extract_section_text({
            'title': 'Engineer',
            'description': 'Developed apps'
        })
        self.assertIn("Engineer", text3)
        self.assertIn("Developed apps", text3)
    
    def test_weighted_scoring(self):
        """Test that section weights are applied correctly."""
        parsed_resume = {
            'summary': 'Short summary.',
            'experience': [{'description': 'Long and detailed experience section with multiple sentences and comprehensive information about work history.'}],
            'skills': ['Python'],
            'education': [{'degree': 'BS CS'}]
        }
        
        result = self.scorer.score_resume_sections(parsed_resume)
        
        # Experience should have significant weight
        self.assertIn('experience', result['section_scores'])
        self.assertGreater(result['overall_language_score'], 0)
    
    def test_grade_assignment(self):
        """Test letter grade assignment."""
        self.assertEqual(self.scorer._score_to_grade(95), "A")
        self.assertEqual(self.scorer._score_to_grade(85), "B")
        self.assertEqual(self.scorer._score_to_grade(75), "C")
        self.assertEqual(self.scorer._score_to_grade(65), "D")
        self.assertEqual(self.scorer._score_to_grade(50), "F")


if __name__ == '__main__':
    unittest.main()