"""
Unit tests for Keyword Optimizer (Phase 6).
"""

import unittest
from src.ats.keyword_optimizer import KeywordOptimizer


class TestKeywordOptimizer(unittest.TestCase):
    """Test keyword optimization functionality."""
    
    def setUp(self):
        """Initialize keyword optimizer for tests."""
        self.optimizer = KeywordOptimizer()
    
    def test_keyword_density_calculation(self):
        """Test keyword density calculation."""
        text = "Python developer with Java experience. Python and Java skills."
        density = self.optimizer._calculate_keyword_density(text)
        
        self.assertGreater(density, 0)
        self.assertLess(density, 1)
    
    def test_role_keyword_matching(self):
        """Test matching against role keywords."""
        text = "Experienced Python developer skilled in Django, REST APIs, and AWS"
        role_keywords = ["Python", "Django", "REST APIs", "AWS", "Docker"]
        
        result = self.optimizer._analyze_role_keywords(text, role_keywords)
        
        self.assertEqual(result['found_count'], 4)
        self.assertEqual(result['missing_count'], 1)
        self.assertIn('Docker', result['missing_keywords'])
        self.assertGreater(result['match_rate'], 0.5)
    
    def test_action_verb_detection(self):
        """Test action verb detection."""
        text = """
        Led development of microservices architecture.
        Developed RESTful APIs using Python.
        Improved system performance by 40%.
        """
        
        result = self.optimizer._analyze_action_verbs(text)
        
        self.assertGreater(result['count'], 0)
        self.assertIn('led', result['verbs'])
        self.assertIn('developed', result['verbs'])
        self.assertIn('improved', result['verbs'])
    
    def test_keyword_stuffing_detection(self):
        """Test detection of keyword stuffing."""
        # Excessive repetition
        stuffed_resume = {
            'summary': 'Python Python Python expert in Python development',
            'experience': [{'description': 'Python Python Python'}]
        }
        
        result = self.optimizer.analyze_keywords(stuffed_resume)
        
        # Should have lower score or warning
        self.assertTrue(
            result['keyword_score'] < 100 or 
            any('stuffing' in issue['issue'].lower() for issue in result['issues'])
        )
    
    def test_keyword_distribution(self):
        """Test keyword distribution analysis."""
        resume = {
            'summary': 'Python developer with AWS experience',
            'experience': [{'description': 'Built microservices using Docker'}],
            'skills': ['Python', 'AWS', 'Docker']
        }
        
        result = self.optimizer.analyze_keywords(resume)
        
        self.assertIn('keyword_distribution', result)
        self.assertFalse(result['keyword_distribution']['concentrated'])
    
    def test_empty_resume(self):
        """Test handling of empty resume."""
        result = self.optimizer.analyze_keywords({})
        
        self.assertEqual(result['keyword_score'], 0)
        self.assertFalse(result['is_optimized'])


if __name__ == '__main__':
    unittest.main()